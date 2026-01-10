from typing import List, Dict, Any
import random
from src.state import get_user_state
from src.recommender.baseline import BaselineRecommender
from src.data_ingestion import load_raw_data
from src.explainability.engine import ExplanationEngine

class FinalRanker:
    def __init__(self):
        self.data = load_raw_data()
        self.items_df = self.data["items"].set_index("item_id")
        self.baseline = BaselineRecommender(self.data["items"])
        self.explainer = ExplanationEngine()

    def rank(self, user_id: str, user_state: Dict[str, Any], candidates: List[str] = None) -> List[Dict[str, Any]]:
        """
        Ranks candidates based on user state (emotion, fatigue).
        Returns list of dicts: {'item_id': str, 'score': float, 'explanation': str}
        """
        
        # 1. Check for hard interventions
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

        # 2. Get candidates if not provided
        if not candidates:
            # Get more than needed to allow for filtering
            candidates = self.baseline.recommend(user_id, top_k=20)
            
        ranked_items = []
        
        # 3. Score each candidate
        for item_id in candidates:
            if item_id not in self.items_df.index:
                continue
                
            item_meta = self.items_df.loc[item_id].to_dict()
            
            # Base score (mock: random + popularity)
            score = 0.5 + (item_meta.get("popularity", 0.5) * 0.5)
            
            # 4. Adjust for Fatigue (Diversity)
            # If fatigue is high, penalize items with same category as recent history
            recent_items = user_state.get("recent_interaction_items", [])
            recent_cats = set()
            for rid in recent_items:
                if rid in self.items_df.index:
                    recent_cats.add(self.items_df.loc[rid]["category"])
            
            if fatigue.get("score", 0.0) > 0.4:
                if item_meta["category"] in recent_cats:
                    score *= 0.5 # Penalize
            
            # 5. Adjust for Emotion
            emotion = user_state.get("emotion", {})
            label = emotion.get("label", "neutral")
            
            # Mock logic: Sad users like Comedy; Happy users like Action
            if label == "sad" and item_meta["category"] == "comedy":
                score *= 1.5
            elif label == "happy" and item_meta["category"] == "action":
                score *= 1.2
            elif label == "bored" and item_meta["category"] in ["thriller", "sci-fi"]:
                score *= 1.3
                
            # 6. Generate Explanation
            explanation = self.explainer.generate_explanation(user_state, item=item_meta, context="recommendation")
            
            ranked_items.append({
                "item_id": item_id,
                "title": item_meta["title"],
                "category": item_meta["category"],
                "score": score,
                "explanation": explanation
            })
            
        # 7. Sort and Return
        ranked_items.sort(key=lambda x: x["score"], reverse=True)
        return ranked_items[:10]
