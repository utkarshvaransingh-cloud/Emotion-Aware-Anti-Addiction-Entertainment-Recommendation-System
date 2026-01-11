from typing import List, Dict, Any, Optional

def calculate_repetition_index(recent_items: List[str], item_metadata: Dict[str, Any]) -> float:
    """
    Calculates how repetitive the recent consumption is.
    returns: 0.0 (diverse) to 1.0 (highly repetitive)
    """
    if not recent_items:
        return 0.0
    
    # Simple heuristic: Ratio of unique items to total items in window
    # In a real system, would use genre/category embeddings similarity.
    # Here checking raw item_id duplication (mocking "similar" as "same")
    
    # Let's try to get categories if item_metadata is passed (assuming item_metadata is keyed by item_id)
    categories = []
    for iid in recent_items:
        if iid in item_metadata:
             categories.append(item_metadata[iid].get("category", "unknown"))
        else:
             categories.append("unknown")
             
    if not categories:
        return 0.0
        
    unique_cats = len(set(categories))
    total = len(categories)
    
    # If all same category -> repetition = 1.0
    # If all different -> repetition = 0.0 (approx)
    repetition = 1.0 - (unique_cats / total)
    return max(0.0, min(1.0, repetition))

def compute_fatigue_score(
    session_duration_minutes: float, 
    repetition_index: float, 
    time_of_day_penalty: float = 0.0
) -> float:
    """
    Computes a composite fatigue score.
    factors:
    - session_duration: logistic growth? or simple linear cap.
    - repetition: linear multiplier.
    - penalty: additive.
    """
    # Normalize session duration (e.g., 2 hours = 1.0 fatigue)
    duration_score = min(1.0, session_duration_minutes / 120.0)
    
    # Weighted Sum - Duration is now primary factor (0.7)
    # This ensures 120+ min session alone gives score >= 0.7
    # Combined with even minimal repetition/night time pushes it over 0.8 threshold
    score = (0.7 * duration_score) + (0.2 * repetition_index) + (0.1 * time_of_day_penalty)
    
    return max(0.0, min(1.0, score))

def get_intervention(fatigue_score: float) -> Optional[str]:
    """
    Returns an intervention strategy based on fatigue.
    """
    if fatigue_score >= 0.7:  # Lowered from 0.8 to match 120min promise
        return "hard_break" # Stop recommendations or show "Take a break" overlay
    elif fatigue_score > 0.5:
        return "soft_break" # Inject "calm" content or generic notification
    elif fatigue_score > 0.3:
        return "diversify" # Force category switch
    return None
