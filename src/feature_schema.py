from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserFeatures(BaseModel):
    user_id: str
    age: int
    gender: Optional[str] = None
    interests: List[str] = []
    historical_preferences: Dict[str, float] = {} # e.g. {"action": 0.8, "comedy": 0.2}

class ItemFeatures(BaseModel):
    item_id: str
    title: str
    category: str
    tags: List[str] = []
    duration_minutes: float
    popularity_score: float = 0.0

class ContextFeatures(BaseModel):
    time_of_day: str # "morning", "afternoon", "evening", "night"
    device_type: str # "mobile", "desktop", "tv"
    location: Optional[str] = None
    session_minutes: Optional[int] = 0 # New: Allow simulating fatigue from frontend
    
class EmotionFeatures(BaseModel):
    valence: float # -1.0 to 1.0
    arousal: float # -1.0 to 1.0
    emotion_label: Optional[str] = None # "happy", "sad", etc.

class AntiAddictionFeatures(BaseModel):
    session_duration_minutes: float
    items_consumed_today: int
    consecutive_similar_items: int
    fatigue_score: float = 0.0
