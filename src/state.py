import pandas as pd
from typing import Dict, Any, Optional, List
import datetime

from src.feature_schema import ContextFeatures, UserFeatures
from src.data_ingestion import load_raw_data
from src.emotion.inference import infer_emotion
from src.anti_addiction import calculate_repetition_index, compute_fatigue_score, get_intervention

# Cache data for now (in a real app, use a database or feature store)
_DATA_CACHE = None

def _get_data():
    global _DATA_CACHE
    if _DATA_CACHE is None:
        _DATA_CACHE = load_raw_data()
    return _DATA_CACHE

def get_user_state(
    user_id: str, 
    context: ContextFeatures, 
    raw_emotion_input: Any = None
) -> Dict[str, Any]:
    """
    Constructs the state vector for a user.
    Aggregates: Profile, Recent History, Current Emotion, Fatigue, Context.
    """
    data = _get_data()
    users_df = data["users"]
    interactions_df = data["interactions"]
    
    # 1. User Profile
    user_row = users_df[users_df["user_id"] == user_id]
    if user_row.empty:
        # Handle new/unknown user
        profile = {
            "age": 25, # default
            "interests": []
        }
    else:
        profile = {
            "age": int(user_row.iloc[0]["age"]),
            "interests": user_row.iloc[0]["interests"].split(",")
        }
        
    # 2. Recent History (Last 5 interactions)
    user_history = interactions_df[interactions_df["user_id"] == user_id].sort_values("timestamp", ascending=False)
    recent_items = user_history.head(5)["item_id"].tolist()
    
    # 3. Emotion
    # If raw input is provided, infer emotion. Otherwise, maybe fetch cached or use neutral.
    if raw_emotion_input:
        emotion_state = infer_emotion(raw_emotion_input)
    else:
        # Default or previous state
        emotion_state = {"valence": 0.0, "arousal": 0.0, "label": "neutral"}
        
    # 4. Context
    context_dict = context.dict()
    
    # 5. Fatigue Calculation (Using Anti-Addiction Module)
    # Prepare metadata for repetition check
    # In a real app, this would be efficient DB lookup. Here we scan the loaded DF.
    items_df = data["items"].set_index("item_id")
    # simplified metadata dict for recent items
    item_meta_subset = {}
    for iid in recent_items:
        if iid in items_df.index:
            item_meta_subset[iid] = items_df.loc[iid].to_dict()
            
    # Use provided session duration from context (frontend simulation) or default mock logic
    session_minutes = context.session_minutes if context.session_minutes is not None and context.session_minutes > 0 else 60
    
    # Calculate repetition based on recent history
    repetition_idx = calculate_repetition_index(recent_items, item_meta_subset)
    
    # Convert time_of_day string to penalty float (night = higher fatigue)
    tod_penalty = 1.0 if context.time_of_day == "night" else 0.0
    
    fatigue_score = compute_fatigue_score(
        session_duration_minutes=session_minutes,
        repetition_index=repetition_idx,
        time_of_day_penalty=tod_penalty
    )
    
    intervention = get_intervention(fatigue_score)

    # Construct State
    state = {
        "user_id": user_id,
        "profile": profile,
        "recent_interaction_items": recent_items,
        "emotion": emotion_state,
        "context": context_dict,
        "fatigue": {
            "score": fatigue_score,
            "intervention": intervention,
            "metrics": {
                "repetition": repetition_idx,
                "session_minutes": session_minutes,
                "tod_penalty": tod_penalty
            }
        }
    }
    
    return state

def to_feature_vector(state: Dict[str, Any]) -> List[float]:
    """
    Converts the state dictionary into a fixed-size numerical vector
    available for machine learning models.
    Structure:
    [
      age (normalized), 
      valence, arousal, 
      fatigue_score, 
      time_of_day_ohe (4 dims), 
      device_type_ohe (2 dims)
    ]
    """
    import numpy as np
    
    vector = []
    
    # User Profile
    # Normalize age (approx 0-100)
    vector.append(state["profile"].get("age", 25) / 100.0)
    
    # Emotion
    vector.append(state["emotion"].get("valence", 0.0))
    vector.append(state["emotion"].get("arousal", 0.0))
    
    # Fatigue
    vector.append(state["fatigue"].get("score", 0.0))
    
    # Context - Time of Day (OHE: morning, afternoon, evening, night)
    tod = state["context"].get("time_of_day", "")
    vector.extend([
        1.0 if tod == "morning" else 0.0,
        1.0 if tod == "afternoon" else 0.0,
        1.0 if tod == "evening" else 0.0,
        1.0 if tod == "night" else 0.0
    ])
    
    # Context - Device (OHE: mobile, desktop)
    dev = state["context"].get("device_type", "")
    vector.extend([
        1.0 if dev == "mobile" else 0.0,
        1.0 if dev == "desktop" else 0.0
    ])
    
    return vector
