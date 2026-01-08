import random
from typing import Dict, Any

def infer_emotion(input_data: Any) -> Dict[str, float]:
    """
    Infers emotion from input data (image bytes, text, etc.).
    Currently returns a mock emotion vector.
    """
    # Mock logic
    # In reality, this would use a model like DeepFace for images or a BERT model for text.
    
    # Randomly simulate an emotion state for testing
    emotions = ["happy", "sad", "neutral", "stressed", "excited"]
    dominant = random.choice(emotions)
    
    result = {
        "valence": 0.0,
        "arousal": 0.0,
        "label": dominant,
        "confidence": 0.85
    }
    
    if dominant == "happy":
        result["valence"] = 0.8
        result["arousal"] = 0.6
    elif dominant == "sad":
        result["valence"] = -0.6
        result["arousal"] = -0.4
    elif dominant == "stressed":
        result["valence"] = -0.7
        result["arousal"] = 0.8
    
    return result
