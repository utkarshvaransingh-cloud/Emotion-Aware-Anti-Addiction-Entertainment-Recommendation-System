from typing import Dict, Any, List

class ExplanationEngine:
    """
    Generates natural language explanations for recommendations and interventions.
    """

    def generate_explanation(
        self, 
        user_state: Dict[str, Any], 
        item: Dict[str, Any] = None, 
        context: str = "recommendation"
    ) -> str:
        """
        Generates a human-readable string explaining the system's decision.
        
        Args:
            user_state: The full user state dictionary (emotion, fatigue, profile, etc.).
            item: The item dictionary being recommended (optional for interventions).
            context: 'recommendation' or 'intervention'.
            
        Returns:
            str: The explanation text.
        """
        
        # 1. Handle Interventions (Fatigue)
        if context == "intervention":
            fatigue_data = user_state.get("fatigue", {})
            intervention_type = fatigue_data.get("intervention")
            
            if intervention_type == "hard_break":
                return "It looks like you've been watching for a while. We suggest taking a short break to refresh!"
            elif intervention_type == "soft_break":
                return "You've been enjoying a lot of similar content. Here are some shorter or different options to keep things fresh."
            elif intervention_type == "diversify":
                return "We noticed you've been watching a lot of the same genre. How about trying something different?"
            else:
                return "We suggest this for your well-being."

        # 2. Handle Recommendations (Content)
        if item:
            emotion = user_state.get("emotion", {})
            label = emotion.get("label", "neutral")
            
            # Emotion-based explanation
            # Simple heuristic: If the ranker boosts based on emotion, we mention it.
            # (In a real system, we'd pass a flag saying "boosted_by_emotion")
            # Here we assume if they are Sad and it's Comedy, that was the reason.
            item_cat = item.get("category", "").lower()
            
            if label == "sad" and item_cat == "comedy":
                return f"Since you might be feeling a bit down, we picked this {item.get('title')} to cheer you up."
            elif label == "happy" and item_cat == "action":
                return f"To match your high energy, here is an exciting Action movie: {item.get('title')}."
            elif label == "bored" and item_cat in ["thriller", "sci-fi"]:
                return f"To wake you up, we found this engaging {item_cat} movie."
                
            # Default / Profile-based
            return f"Because you enjoy {item.get('category')} movies."
            
        return "Recommended for you."
