import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.anti_addiction import calculate_repetition_index, compute_fatigue_score, get_intervention
from src.state import get_user_state
from src.feature_schema import ContextFeatures

class TestPhase5Addiction(unittest.TestCase):
    
    def test_repetition_logic(self):
        print("\n[Phase 5] Testing Repetition Logic...")
        # Scenario 1: All same category
        items = ["i1", "i2", "i3"]
        meta = {
            "i1": {"category": "action"},
            "i2": {"category": "action"},
            "i3": {"category": "action"}
        }
        idx = calculate_repetition_index(items, meta)
        print(f"  - Repetition Index (All Action): {idx}")
        self.assertAlmostEqual(idx, 0.66, delta=0.1) # 1 - 1/3 = 0.66
        
        # Scenario 2: Diverse
        meta_diverse = {
            "i1": {"category": "action"},
            "i2": {"category": "comedy"},
            "i3": {"category": "romance"}
        }
        idx_div = calculate_repetition_index(items, meta_diverse)
        print(f"  - Repetition Index (Diverse): {idx_div}")
        self.assertEqual(idx_div, 0.0) # 1 - 3/3 = 0.0

    def test_fatigue_score_and_intervention(self):
        print("\n[Phase 5] Testing Fatigue & Intervention...")
        # Case A: Low fatigue
        score_low = compute_fatigue_score(session_duration_minutes=10, repetition_index=0.0, time_of_day_penalty=0.0)
        print(f"  - Score (10m, diverse, day): {score_low}")
        self.assertLess(score_low, 0.2)
        self.assertIsNone(get_intervention(score_low))
        
        # Case B: High fatigue (2 hours, repetitive, night)
        score_high = compute_fatigue_score(session_duration_minutes=120, repetition_index=1.0, time_of_day_penalty=1.0)
        print(f"  - Score (120m, repet, night): {score_high}")
        self.assertGreater(score_high, 0.8)
        self.assertEqual(get_intervention(score_high), "hard_break")

    def test_integration_in_state(self):
        print("\n[Phase 5] Testing State Integration...")
        ctx = ContextFeatures(time_of_day="night", device_type="mobile")
        # u_1 has history in our mock data
        state = get_user_state("u_1", ctx)
        
        self.assertIn("fatigue", state)
        self.assertIn("score", state["fatigue"])
        self.assertIn("intervention", state["fatigue"])
        print(f"  - User State Fatigue: {state['fatigue']}")

if __name__ == '__main__':
    unittest.main()
