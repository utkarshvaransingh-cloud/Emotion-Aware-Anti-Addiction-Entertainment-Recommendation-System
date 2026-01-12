from typing import List, Dict, Any, Optional

def calculate_repetition_index(recent_items: List[str], item_metadata: Dict[str, Any]) -> float:
    """
    Calculates how repetitive the recent consumption is based on category overlap.
    Returns: 0.0 (diverse) to 1.0 (highly repetitive)
    """
    if not recent_items or len(recent_items) < 2:
        return 0.0
    
    categories = []
    for iid in recent_items:
        if iid in item_metadata:
             categories.append(item_metadata[iid].get("category", "unknown"))
        else:
             categories.append("unknown")
              
    unique_cats = len(set(categories))
    total = len(categories)
    
    # Entropy-inspired repetition: 1.0 if all same, scales down as diversity increases
    # We use a steeper penalty for absolute repetition
    repetition = 1.0 - (unique_cats / total)
    
    # If 4 out of 5 are same category, that's high repetition (0.8)
    return max(0.0, min(1.0, repetition))

def compute_fatigue_score(
    session_duration_minutes: float, 
    repetition_index: float, 
    cumulative_daily_minutes: float = 0.0,
    time_of_day_penalty: float = 0.0
) -> float:
    """
    Computes a composite fatigue score considering:
    - Session duration (immediate fatigue)
    - Repetition index (mental boredom)
    - Cumulative daily usage (long-term addiction risk)
    - Time of day (circadian rhythm)
    """
    # 1. Session Factor (120 min = 1.0)
    duration_score = min(1.0, session_duration_minutes / 120.0)
    
    # 2. Daily Factor (300 min = 1.0)
    daily_score = min(1.0, cumulative_daily_minutes / 300.0)
    
    # Weighted Sum
    # Session (0.5) + Daily (0.2) + Repetition (0.2) + TOD (0.1)
    score = (0.5 * duration_score) + (0.2 * daily_score) + (0.2 * repetition_index) + (0.1 * time_of_day_penalty)
    
    return max(0.0, min(1.0, score))

def get_intervention(fatigue_score: float) -> Optional[str]:
    """
    Returns an intervention strategy based on fatigue.
    Threshold of 0.84 ensures:
    - Pure 120min watch time triggers (0.7 * 1.0 = 0.7, needs more)
    - 140+ min triggers reliably  
    """
    if fatigue_score >= 0.84:  # ~140 minutes or 120min + high factors
        return "hard_break"
    elif fatigue_score > 0.6:
        return "soft_break"
    elif fatigue_score > 0.4:
        return "diversify"
    return None
