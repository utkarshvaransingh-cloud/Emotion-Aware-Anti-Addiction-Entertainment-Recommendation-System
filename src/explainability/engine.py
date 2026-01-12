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
            return self._explain_intervention(user_state)
        elif context == "recommendation" and item:
            return self._explain_recommendation(user_state, item)
        else:
            return "Based on your current preferences."
    
    def _explain_intervention(self, user_state: Dict[str, Any]) -> str:
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

    def _explain_recommendation(self, user_state: Dict[str, Any], item: Dict[str, Any]) -> str:
        emotion_label = user_state.get("emotion", {}).get("label", "neutral")
        category = item.get("category", "unknown")
        time_of_day = user_state.get("context", {}).get("time_of_day", "evening")
        
        # Emotion-based explanations
        emotion_reasons = {
            ("sad", "comedy"): "Because you're feeling down, we picked this comedy to cheer you up! 😊",
            ("sad", "romance"): "We thought this heartwarming story might lift your spirits. 💕",
            ("anxious", "doc"): "Since you're feeling anxious, this calm documentary might help you relax. 🧘",
            ("anxious", "animation"): "To help ease your anxiety, we recommend this soothing animated film. 🎨",
            ("happy", "action"): "You're in a great mood! This high-energy action film matches your vibe! ⚡",
            ("happy", "adventure"): "Perfect for your happy mood - an exciting adventure awaits! 🗺️",
            ("bored", "thriller"): "Feeling bored? This thriller will definitely keep you on the edge of your seat! 🔥",
            ("bored", "sci-fi"): "We picked this mind-bending sci-fi to cure your boredom! 🚀",
            ("bored", "mystery"): "This mysterious plot will capture your attention! 🕵️",
            ("neutral", "drama"): "A balanced choice for your current calm mood. 🎭",
            ("neutral", "music"): "Something light and musical for your neutral vibe. 🎵"
        }
        
        # Time-based reasons
        time_reasons = {
            ("morning", "doc"): "Perfect morning watch - informative yet relaxing. ☀️",
            ("morning", "animation"): "A light, uplifting choice to start your day! 🌅",
            ("night", "thriller"): "Late-night thrill - perfect for evening viewing! 🌙",
            ("night", "horror"): "Night time is the right time for some scares! 👻",
            ("night", "mystery"): "Late night mystery - the perfect bedtime story! 🌃",
            ("afternoon", "comedy"): "Afternoon pick-me-up with some laughs! ☕",
            ("afternoon", "romance"): "A sweet afternoon escape with this romantic story. 💐",
            ("evening", "drama"): "A classic evening drama to wind down. 🍿"
        }
        
        # Check for emotion match
        if (emotion_label, category) in emotion_reasons:
            return emotion_reasons[(emotion_label, category)]
        
        # Check for time match
        if (time_of_day, category) in time_reasons:
            return time_reasons[(time_of_day, category)]
        
        # Collaborative/ML reason
        if user_state.get("profile", {}).get("age", 0) > 0:
             return f"Based on your profile and our {emotion_label} vibe detection. ✨"
             
        # Default based on genre preference
        return f"Matched for your current {time_of_day} session. 🎬"
