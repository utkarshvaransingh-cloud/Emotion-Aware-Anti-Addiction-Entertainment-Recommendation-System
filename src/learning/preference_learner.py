"""
Preference Learning Module
Analyzes user interaction history to learn personalized preferences.
"""
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
import numpy as np

class PreferenceLearner:
    """
    Learns user preferences from interaction history and pre-trained models.
    Analyzes patterns in mood, time of day, and genre combinations.
    """
    
    def __init__(self, interactions_file: str = None, model_file: str = None):
        if interactions_file is None:
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            interactions_file = data_dir / "interactions.json"
        
        if model_file is None:
            project_root = Path(__file__).parent.parent.parent
            model_file = project_root / "models" / "genre_preferences.pkl"
        
        self.interactions_file = Path(interactions_file)
        self.model_file = Path(model_file)
        self.interactions = self._load_interactions()
        self.trained_model = self._load_trained_model()
    
    def _load_interactions(self) -> List[Dict[str, Any]]:
        """Load interaction history from JSON file."""
        if not self.interactions_file.exists():
            return []
        
        try:
            with open(self.interactions_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def _load_trained_model(self) -> Dict[str, Any]:
        """Load pre-trained genre preference model."""
        if not self.model_file.exists():
            print(f"⚠️ Pre-trained model not found at {self.model_file}")
            return None
        
        try:
            with open(self.model_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate learned preferences for a specific user.
        Combines real-time interaction history with pre-trained model data.
        """
        # 1. Start with pre-trained preferences if available
        user_prefs = self._default_preferences()
        
        if self.trained_model:
            # Handle user_id with 'u_' prefix or as raw integer
            numeric_user_id = None
            try:
                if str(user_id).startswith('u_'):
                    numeric_user_id = int(user_id.split('_')[1])
                else:
                    numeric_user_id = int(user_id)
                
                if numeric_user_id and numeric_user_id in self.trained_model.get('user_preferences', {}):
                    user_prefs['favorite_genres'] = self.trained_model['user_preferences'][numeric_user_id].copy()
            except (ValueError, TypeError, IndexError):
                pass
            
            # Use global preferences as baseline if user-specific ones not found
            if not user_prefs['favorite_genres'] and 'global_preferences' in self.trained_model:
                user_prefs['favorite_genres'] = self.trained_model['global_preferences'].copy()

        # 2. Overlay with real-time interactions
        user_interactions = [i for i in self.interactions if str(i.get('user_id')) == str(user_id)]
        
        if not user_interactions:
            return user_prefs
        
        # Track stats from local history
        local_genre_watches = Counter()
        local_genre_completions = defaultdict(int)
        emotion_genre = defaultdict(lambda: Counter())
        time_genre = defaultdict(lambda: Counter())
        total_completed = 0
        
        for interaction in user_interactions:
            movie_id = interaction.get('movie_id', '')
            emotion = interaction.get('emotion', 'neutral')
            time_of_day = interaction.get('time_of_day', 'evening')
            completed = interaction.get('completed', False)
            duration_watched = interaction.get('duration_watched', 0)
            movie_duration = interaction.get('movie_duration', 120)
            
            genre = self._infer_genre_from_id(movie_id)
            
            local_genre_watches[genre] += 1
            if completed or (duration_watched / movie_duration > 0.8):
                local_genre_completions[genre] += 1
                total_completed += 1
            
            emotion_genre[emotion][genre] += 1
            time_genre[time_of_day][genre] += 1
        
        # Merge local favorite genres with pre-trained ones
        # We give weight to local history (50/50 blend for this version)
        for genre, count in local_genre_watches.items():
            local_score = local_genre_completions[genre] / count
            if genre in user_prefs['favorite_genres']:
                user_prefs['favorite_genres'][genre] = (user_prefs['favorite_genres'][genre] + local_score) / 2.0
            else:
                user_prefs['favorite_genres'][genre] = local_score
        
        # Emotion-Genre affinity
        for emotion, genres in emotion_genre.items():
            total_emotion_watches = sum(genres.values())
            user_prefs['emotion_genre_affinity'][emotion] = {
                genre: count / total_emotion_watches
                for genre, count in genres.items()
            }
        
        # Time-Genre affinity
        for time, genres in time_genre.items():
            total_time_watches = sum(genres.values())
            user_prefs['time_genre_affinity'][time] = {
                genre: count / total_time_watches
                for genre, count in genres.items()
            }
        
        user_prefs['total_watches'] = len(user_interactions)
        user_prefs['completion_rate'] = total_completed / len(user_interactions) if len(user_interactions) > 0 else 0
        
        return user_prefs
    
    def _infer_genre_from_id(self, movie_id: str) -> str:
        """Infer genre from movie ID (based on our data structure)."""
        try:
            num = int(movie_id.split('_')[1])
            if 1 <= num <= 10: return 'action'
            elif 11 <= num <= 18: return 'romance'
            elif 19 <= num <= 26: return 'comedy'
            elif 27 <= num <= 34: return 'sci-fi'
            elif 35 <= num <= 37: return 'doc'
            elif 38 <= num <= 40: return 'thriller'
            elif 41 <= num <= 45: return 'fantasy'
            elif 46 <= num <= 50: return 'horror'
            elif 51 <= num <= 55: return 'mystery'
            elif 56 <= num <= 60: return 'drama'
            elif 61 <= num <= 65: return 'adventure'
            elif 66 <= num <= 70: return 'animation'
            elif 71 <= num <= 75: return 'musical'
            elif 76 <= num <= 80: return 'crime'
            else: return 'unknown'
        except:
            return 'unknown'
    
    def _default_preferences(self) -> Dict[str, Any]:
        """Return default preferences for new users."""
        return {
            'favorite_genres': {},
            'emotion_genre_affinity': {},
            'time_genre_affinity': {},
            'completion_rate': 0.0,
            'total_watches': 0
        }
    
    def calculate_personalization_boost(
        self, 
        user_id: str, 
        item_genre: str, 
        current_emotion: str, 
        current_time: str
    ) -> float:
        """
        Calculate boost multiplier for an item based on learned preferences.
        
        Returns: float between 0.5 (strong negative signal) to 2.0 (strong positive signal)
        """
        prefs = self.get_user_preferences(user_id)
        
        # If no history, return neutral
        if prefs['total_watches'] == 0:
            return 1.0
        
        boost = 1.0
        
        # Factor 1: Favorite genres (completion rate)
        if item_genre in prefs['favorite_genres']:
            completion_affinity = prefs['favorite_genres'][item_genre]
            # High completion rate → boost, low → penalty
            boost *= (0.5 + completion_affinity * 1.5)  # Range: 0.5 to 2.0
        
        # Factor 2: Emotion-Genre pattern
        if current_emotion in prefs['emotion_genre_affinity']:
            emotion_genres = prefs['emotion_genre_affinity'][current_emotion]
            if item_genre in emotion_genres:
                # They've watched this genre in this mood before
                boost *= (1.0 + emotion_genres[item_genre])  # Up to 2x boost
        
        # Factor 3: Time-Genre pattern
        if current_time in prefs['time_genre_affinity']:
            time_genres = prefs['time_genre_affinity'][current_time]
            if item_genre in time_genres:
                boost *= (1.0 + time_genres[item_genre] * 0.5)  # Up to 1.5x boost
        
        # Cap the boost to reasonable range
        return np.clip(boost, 0.3, 2.5)
