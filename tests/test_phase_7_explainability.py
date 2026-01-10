import unittest
from src.state import get_user_state
from src.recommender.final_ranker import FinalRanker
from src.explainability.engine import ExplanationEngine

# Mock classes to avoid full DB dependency
class MockBaseline:
    def recommend(self, user_id, top_k=10):
        return ["i_1", "i_2", "i_3"] # Assumes these exist in mock data

class TestExplainability(unittest.TestCase):
    
    def setUp(self):
        self.ranker = FinalRanker()
        self.engine = ExplanationEngine()
        
    def test_intervention_explanation(self):
        """Test explanation for hard break"""
        # Formulate a state with Hard Break
        state = {
            "fatigue": {"intervention": "hard_break", "score": 1.0}
        }
        explanation = self.engine.generate_explanation(state, context="intervention")
        print(f"\n[XAI] Intervention Explanation: {explanation}")
        self.assertIn("break", explanation.lower())
        
    def test_emotion_explanation_sad_comedy(self):
        """Test explanation for Sad user + Comedy item"""
        state = {"emotion": {"label": "sad"}}
        item = {"title": "Funny Movie", "category": "comedy"}
        
        explanation = self.engine.generate_explanation(state, item=item, context="recommendation")
        print(f"[XAI] Sad->Comedy Explanation: {explanation}")
        self.assertIn("cheer you up", explanation.lower())
        
    def test_emotion_explanation_happy_action(self):
        """Test explanation for Happy user + Action item"""
        state = {"emotion": {"label": "happy"}}
        item = {"title": "Explosion Movie", "category": "action"}
        
        explanation = self.engine.generate_explanation(state, item=item, context="recommendation")
        print(f"[XAI] Happy->Action Explanation: {explanation}")
        self.assertIn("high energy", explanation.lower())
        
    def test_ranker_integration(self):
        """Test that FinalRanker returns items with 'explanation' field"""
        # Mock state
        # We need to rely on the ranker's internal data loading for item metadata
        # Let's just run rank() with a mock user
        
        # User 1 is usually in the mock data
        results = self.ranker.rank("u_1", context={"time_of_day": "evening", "device": "mobile"})
        
        if results:
            first_item = results[0]
            print(f"[XAI] Ranker Output Item 1: {first_item}")
            self.assertIn("explanation", first_item)
            self.assertIsInstance(first_item["explanation"], str)
            self.assertNotEqual(first_item["explanation"], "")

if __name__ == "__main__":
    unittest.main()
