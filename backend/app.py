from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import sys
import os
import datetime
import json
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.feature_schema import ContextFeatures, EmotionFeatures
from src.state import get_user_state
from src.recommender.final_ranker import FinalRanker
from src.data_ingestion import load_raw_data
from backend.schemas.recommend import RecommendRequest

# Global ranker variable
ranker = None

# Create a persistent log file we can actually read
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/server_debug.log"))

# User storage file
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    USERS_FILE.parent.mkdir(exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Force UTF-8 encoding for Windows and replace problematic characters if necessary
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception as e:
        print(f"Logging error: {e}")
    
    # Print might still fail on some Windows terminals, so we handle it
    try:
        print(msg)
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ranker
    log_message("\n" + "-"*30)
    log_message("SERVER STARTUP: Loading Data...")
    log_message("-"*30)
    try:
        ranker = FinalRanker()
        log_message("SUCCESS: Recommendation Engine Ready.")
    except Exception as e:
        import traceback
        log_message(f"CRITICAL ERROR: Ranker failed to start: {e}\n{traceback.format_exc()}")
    log_message("-"*30 + "\n")
    yield

app = FastAPI(
    title="Emotion-Aware RecSys API",
    description="Anti-Addiction Entertainment Recommendation System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Request Models
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
    if ranker is None:
        return {"status": "starting", "message": "Ranker is still initializing..."}
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
    if ranker is None:
        raise HTTPException(status_code=503, detail="Ranker service starting or failed")
    try:
        # 1. Build State
        raw_emotion = request.emotion if request.emotion else None
        
        state = get_user_state(request.user_id, request.context, raw_emotion)
        
        # 2. Get Ranker Output (Pass genre filter)
        log_message(f"Ranking for User: {request.user_id} with genre={request.genre_filter}")
        recommendations = ranker.rank(request.user_id, state, genre_filter=request.genre_filter)
        
        # Convert fatigue metrics to native Python types (avoid numpy serialization issues)
        fatigue_metrics = state["fatigue"].get("metrics", {})
        clean_metrics = {}
        for k, v in fatigue_metrics.items():
            if hasattr(v, 'item'):  # numpy scalar
                clean_metrics[k] = v.item()
            elif isinstance(v, (int, float, str, bool, type(None))):
                clean_metrics[k] = v
            else:
                clean_metrics[k] = float(v) if v is not None else None
        
        return {
            "user_id": request.user_id,
            "recommendations": recommendations,
            "meta": {
                "fatigue_score": float(state["fatigue"].get("score", 0.0)),
                "fatigue_intervention": state["fatigue"].get("intervention"),
                "fatigue_metrics": clean_metrics,
                "detected_emotion": state["emotion"].get("label")
            }
        }
    except Exception as e:
        import traceback
        log_message(f"ERROR in /recommend: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log_interaction")
def log_interaction(interaction: Dict[str, Any] = Body(...)):
    """
    Log user interaction (watch history) for ML training.
    """
    try:
        import json
        from pathlib import Path
        
        # Ensure data directory exists
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        interactions_file = data_dir / "interactions.json"
        
        if interactions_file.exists():
            with open(interactions_file, 'r') as f:
                interactions = json.load(f)
        else:
            interactions = []
        
        interactions.append(interaction)
        
        with open(interactions_file, 'w') as f:
            json.dump(interactions, f, indent=2)
        
        return {"status": "logged", "total_interactions": len(interactions)}
    except Exception as e:
        import traceback
        log_message(f"ERROR in /log_interaction: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to log interaction: {str(e)}")

@app.post("/user/{user_id}/state")
def get_current_user_state(user_id: str, context: ContextFeatures, emotion: Optional[Dict[str, Any]] = None):
    """
    Debug endpoint to view the calculated internal state.
    """
    try:
        state = get_user_state(user_id, context, emotion)
        return state
    except Exception as e:
        import traceback
        log_message(f"ERROR in /user/state: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import socket

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    log_message("\n" + "="*50)
    log_message("       SERVER STARTUP SEQUENCE")
    log_message("="*50)
    
    port = 8080
    if is_port_in_use(port):
        log_message("ERROR: Port 8080 is ALREADY IN USE!")
        log_message("Please close other command prompts running the backend.")
    else:
        log_message("Port 8080 is available.")
    
    log_message("Dashboard Local Link: http://127.0.0.1:8080")
    log_message("==================================================" + "\n")

    # Use 127.0.0.1 strictly. Do NOT use 0.0.0.0 as it confuses browsers on Windows.
    uvicorn.run(app, host="127.0.0.1", port=port)
