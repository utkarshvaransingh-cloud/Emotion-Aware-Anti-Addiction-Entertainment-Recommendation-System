from typing import List, Dict, Any
import random
from src.state import get_user_state
from src.recommender.baseline import BaselineRecommender
from src.data_ingestion import load_raw_data
from src.explainability.engine import ExplanationEngine
from src.learning.preference_learner import PreferenceLearner

class FinalRanker:
    def __init__(self):
        self.data = load_raw_data()
        self.items_df = self.data["items"].set_index("item_id")
        self.baseline = BaselineRecommender(self.data["items"])
        self.explainer = ExplanationEngine()
        self.learner = PreferenceLearner()  # ML Learning System

    def rank(self, user_id: str, user_state: Dict[str, Any], candidates: List[str] = None, genre_filter: str = None) -> List[Dict[str, Any]]:
        """
        Ranks candidates based on user state (emotion, fatigue).
        Returns list of dicts: {'item_id': str, 'score': float, 'explanation': str}
        """
        # 1. Candidate Selection
        # If user explicitly filters by genre, we MUST fetch items from that genre,
        # ignoring the user's history-biased baseline (Exploration Mode).
        if genre_filter and genre_filter.lower() != "all":
            # Filter items by category
            candidates = self.items_df[self.items_df['category'].str.lower() == genre_filter.lower()].index.tolist()
            if not candidates:
                return [] # No items exist for this genre at all
        elif candidates is None:
            # Standard Mode: personalised candidates
            # Get more than needed to allow for filtering
            candidates = self.baseline.recommend(user_id, top_k=20)

        # 2. Case 1: Hard Break Intervention
        fatigue = user_state.get("fatigue", {})
        if fatigue.get("intervention") == "hard_break":
            explanation = self.explainer.generate_explanation(user_state, context="intervention")
            return [{
                "item_id": "BREAK_ACTIVITY",
                "title": "Time for a break!",
                "score": 100.0,
                "explanation": explanation,
                "type": "intervention"
            }]

        # 3. Get candidates if not provided
        if not candidates:
            # Get more than needed to allow for filtering
            candidates = self.baseline.recommend(user_id, top_k=20)
            
        ranked_items = []
        intervention_type = fatigue.get("intervention")
        
        # 4. Score each candidate
        for item_id in candidates:
            if item_id not in self.items_df.index:
                continue
            
            item_meta = self.items_df.loc[item_id].to_dict()
            
            # Genre Filter Check
            if genre_filter and genre_filter.lower() != "all":
                if item_meta["category"].lower() != genre_filter.lower():
                    continue
            
            # Base score (mock: random + popularity)
            score = 0.5 + (item_meta.get("popularity", 0.5) * 0.5)
            
            # 5. Adjust for Fatigue (Diversity & Anti-Addiction)
            recent_items = user_state.get("recent_interaction_items", [])
            recent_cats = set()
            for rid in recent_items:
                if rid in self.items_df.index:
                    recent_cats.add(self.items_df.loc[rid]["category"])
            
            fatigue_score = fatigue.get("score", 0.0)
            item_genre = item_meta.get("category", "unknown")
            
            # A. Penalty for repetitive genres
            if fatigue_score > 0.4:
                if item_genre in recent_cats:
                    # Penalize harder as fatigue grows
                    penalty = 0.5 * (fatigue_score + 0.5)
                    score /= penalty
            
            # B. Soft Break / Diversify Intervention
            if intervention_type in ["soft_break", "diversify"]:
                if item_genre in recent_cats:
                    score *= 0.3 # Strong penalty to force diversity
                else:
                    score *= 1.5 # Boost novel genres
            
            # C. Binge-prevention: Penalize very popular/addictive content if fatigue is rising
            if fatigue_score > 0.6:
                popularity = item_meta.get("popularity", 0.5)
                if popularity > 0.8:
                    score *= (1.1 - fatigue_score) # Dampen high-popularity items

            # 6. Emotion Adjustment - Strong mood-based recommendations
            emotion_label = user_state.get("emotion", {}).get("label", "neutral")
            
            # Define genre preferences for each mood
            mood_boosts = {
                "happy": {
                    "boost": ["action", "adventure", "comedy", "musical", "animation"],  # +3x
                    "good": ["sci-fi", "fantasy"],  # +1.5x
                    "avoid": ["horror", "thriller", "drama"]  # -0.3x
                },
                "sad": {
                    "boost": ["comedy", "romance", "animation", "musical"],  # +3x - cheer up content
                    "good": ["drama", "fantasy"],  # +1.5x
                    "avoid": ["horror", "thriller", "action"]  # -0.3x
                },
                "bored": {
                    "boost": ["thriller", "sci-fi", "mystery", "horror", "action"],  # +3x - exciting content
                    "good": ["adventure", "crime"],  # +1.5x
                    "avoid": ["doc", "drama", "romance"]  # -0.3x
                },
                "anxious": {
                    "boost": ["doc", "animation", "comedy", "romance"],  # +3x - calming content
                    "good": ["drama", "musical", "fantasy"],  # +1.5x
                    "avoid": ["horror", "thriller", "action", "mystery"]  # -0.3x
                },
                "neutral": {
                    "boost": ["comedy", "action", "adventure"],  # +2x - popular choices
                    "good": ["drama", "sci-fi", "romance"],  # +1.3x
                    "avoid": []  # no penalties for neutral
                }
            }
            
            # Apply emotion-based scoring
            if emotion_label in mood_boosts:
                prefs = mood_boosts[emotion_label]
                if item_genre in prefs.get("boost", []):
                    score *= 3.0  # Strong boost for preferred genres
                elif item_genre in prefs.get("good", []):
                    score *= 1.8  # Moderate boost
                elif item_genre in prefs.get("avoid", []):
                    score *= 0.3  # Strong penalty for avoided genres
                # else: no change for neutral genres
            
            # Time-of-day adjustments
            time_of_day = user_state.get("context", {}).get("time_of_day", "evening")
            if time_of_day == "morning" and item_genre in ["doc", "animation"]:
                score *= 1.6
            elif time_of_day == "night" and item_genre in ["thriller", "horror", "mystery"]:
                score *= 1.8
            elif time_of_day == "afternoon" and item_genre in ["comedy", "romance"]:
                score *= 1.5
                
            # 7. ML Personalization Boost
            personalization_multiplier = self.learner.calculate_personalization_boost(
                user_id=user_id,
                item_genre=item_genre,
                current_emotion=emotion_label,
                current_time=time_of_day
            )
            score *= personalization_multiplier
                
            # 8. Generate Explanation
            explanation = self.explainer.generate_explanation(user_state, item=item_meta, context="recommendation")
            
            ranked_items.append({
                "item_id": item_id,
                "title": item_meta.get("title", item_id),
                "category": str(item_genre),
                "score": float(score),
                "explanation": explanation,
                "tmdb_id": item_meta.get("tmdb_id", None),
                "poster_path": item_meta.get("poster_path", None)
            })
            
        # 9. Sort and Return
        ranked_items.sort(key=lambda x: x["score"], reverse=True)
        return ranked_items[:10]
