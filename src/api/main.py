from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
import os
import json
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.feature_schema import ContextFeatures, EmotionFeatures
from src.state import get_user_state
from src.recommender.final_ranker import FinalRanker
from src.data_ingestion import load_raw_data

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Emotion-Aware RecSys API",
    description="Anti-Addiction Entertainment Recommendation System",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ranker (Mock Data Load)
# In production, this might load heavy models.
ranker = FinalRanker()

# User storage file
USERS_FILE = Path(__file__).parent.parent.parent / "data" / "users.json"

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    USERS_FILE.parent.mkdir(exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

class RecommendRequest(BaseModel):
    user_id: str
    context: ContextFeatures
    emotion: Optional[Dict[str, Any]] = None # Optional raw emotion override
    genre_filter: Optional[str] = None # New User Request: Access specific Genres

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    user_id: Optional[str] = None
    name: str
    email: str
    password: str
    interests: Optional[str] = "action,comedy"
    age: Optional[int] = 25

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "rec-sys-api"}

@app.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate user with email and password."""
    users = load_users()
    user = next((u for u in users if u.get('email') == request.email), None)
    
    if user and user.get('password') == request.password:
        return {
            "success": True,
            "user": {
                "user_id": user.get('user_id', 'u_1'),
                "name": user.get('name', 'User'),
                "email": user.get('email')
            }
        }
    
    # Demo fallback: allow any login
    return {
        "success": True,
        "user": {
            "user_id": "u_1",
            "name": request.email.split('@')[0].title(),
            "email": request.email
        }
    }

@app.post("/auth/register")
def register(request: RegisterRequest):
    """Register a new user."""
    users = load_users()
    
    # Check if email exists
    if any(u.get('email') == request.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "user_id": request.user_id or f"u_{len(users) + 1}",
        "name": request.name,
        "email": request.email,
        "password": request.password,
        "interests": request.interests,
        "age": request.age
    }
    
    users.append(new_user)
    save_users(users)
    
    return {"success": True, "user_id": new_user["user_id"]}

@app.post("/recommend")
def get_recommendations(request: RecommendRequest):
    """
    Get personalized recommendations based on user state, emotion, and fatigue.
    """
    try:
        # 1. Build State
        # API clients might send simple dict for emotion, valid enough for our mock
        # If real emotion inference is needed, it happens inside get_user_state via 'infer_emotion'
        raw_emotion = request.emotion if request.emotion else None
        
        state = get_user_state(request.user_id, request.context, raw_emotion)
        
        # 2. Get Ranker Output (Pass genre filter)
        recommendations = ranker.rank(request.user_id, state, genre_filter=request.genre_filter)
        
        return {
            "user_id": request.user_id,
            "recommendations": recommendations,
            "meta": {
                "fatigue_score": state["fatigue"].get("score", 0.0),
                "fatigue_intervention": state["fatigue"].get("intervention"),
                "fatigue_metrics": state["fatigue"].get("metrics", {}),
                "detected_emotion": state["emotion"].get("label")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log_interaction")
def log_interaction(interaction: Dict[str, Any] = Body(...)):
    """
    Log user interaction (watch history) for ML training.
    Stores: user_id, movie_id, emotion, time_of_day, duration_watched, etc.
    """
    try:
        import json
        from pathlib import Path
        
        # Ensure data directory exists
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        interactions_file = data_dir / "interactions.json"
        
        # Load existing interactions
        if interactions_file.exists():
            with open(interactions_file, 'r') as f:
                interactions = json.load(f)
        else:
            interactions = []
        
        # Append new interaction
        interactions.append(interaction)
        
        # Save back
        with open(interactions_file, 'w') as f:
            json.dump(interactions, f, indent=2)
        
        return {"status": "logged", "total_interactions": len(interactions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log interaction: {str(e)}")

@app.post("/user/{user_id}/state")
def get_current_user_state(user_id: str, context: ContextFeatures, emotion: Optional[Dict[str, Any]] = None):
    """
    Debug endpoint to view the calculated internal state (Fatigue, Emotion, etc.)
    """
    try:
        state = get_user_state(user_id, context, emotion)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use 127.0.0.1 for Windows compatibility so clickable links work
    uvicorn.run(app, host="127.0.0.1", port=8000)
