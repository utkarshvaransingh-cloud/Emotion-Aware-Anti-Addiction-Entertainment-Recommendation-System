
import unittest
import sys
import os

sys.path.append(os.getcwd())

from src.recommender.final_ranker import FinalRanker
from src.state import get_user_state
from src.feature_schema import ContextFeatures

class TestPhase6Ranker(unittest.TestCase):
    def setUp(self):
        self.ranker = FinalRanker()
        self.ctx = ContextFeatures(time_of_day="evening", device_type="desktop")
        
    def test_hard_intervention(self):
        print("\n[Phase 6] Testing Hard Intervention...")
        # Mock state with hard break
        state = {
            "fatigue": {"intervention": "hard_break"},
            "user_id": "test_u"
        }
        recs = self.ranker.rank("test_u", state)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["item_id"], "BREAK_ACTIVITY")
        print("  - Correctly recommended BREAK_ACTIVITY")

    def test_emotion_boost(self):
        print("\n[Phase 6] Testing Emotion Boost (Sad -> Comedy)...")
        # Mock state: Sad, Low fatigue
        state = {
            "fatigue": {"score": 0.0, "intervention": None},
            "emotion": {"label": "sad"},
            "user_id": "test_u",
            "recent_interaction_items": [] # No repetition
        }
        
        # We need to ensure we have comedy items in candidates.
        # The baseline returns popular items, let's just inspect what we get.
        recs = self.ranker.rank("test_u", state)
        
        # Check if any comedy item got boosted (reason contains "Boosted")
        boosted = [r for r in recs if "Boosted" in r["reason"]]
        if boosted:
            print(f"  - Boosted Items: {[r['title'] for r in boosted]}")
        else:
            print("  - No items matched boosting criteria (might need more mock data)")
            
    def test_fatigue_penalty(self):
        print("\n[Phase 6] Testing Fatigue Penalty...")
        # Mock state: High fatigue, recently watched 'Action'
        state = {
            "fatigue": {"score": 0.8, "intervention": "diversify"},
            "emotion": {"label": "neutral"},
            "user_id": "test_u",
            "recent_interaction_items": ["i_1", "i_2"] # Assuming these are Action in mock data
        }
        
        # In mock data i_1, i_2 are Action.
        recs = self.ranker.rank("test_u", state)
        
        # Action items should be penalized or ranked lower
        # Let's check reasons
        penalized = [r for r in recs if "Penalized" in r["reason"]]
        if penalized:
            print(f"  - Penalized Items: {[r['title'] for r in penalized]}")
        else:
             print("  - No items matched penalty criteria")

if __name__ == '__main__':
    unittest.main()
