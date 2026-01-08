
import sys
import os
import unittest
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import load_raw_data, process_data
from src.recommender.baseline import BaselineRecommender
from src.emotion.inference import infer_emotion
from src.state import get_user_state, to_feature_vector
from src.feature_schema import ContextFeatures

class TestPhases(unittest.TestCase):
    
    def test_phase_1_data_ingestion(self):
        print("\n[Phase 1] Testing Data Ingestion...")
        raw = load_raw_data()
        self.assertIn("users", raw)
        self.assertIn("items", raw)
        self.assertIn("interactions", raw)
        print(f"  - Loaded {len(raw['users'])} users, {len(raw['items'])} items.")
        
        processed = process_data(raw)
        self.assertEqual(len(processed["users"]), len(raw["users"]))
        print("  - Data processing smoke test passed.")

    def test_phase_2_baseline_recommender(self):
        print("\n[Phase 2] Testing Baseline Recommender...")
        raw = load_raw_data()
        recommender = BaselineRecommender(raw["items"])
        
        recs = recommender.recommend("u_1", top_k=3)
        self.assertEqual(len(recs), 3)
        print(f"  - Top 3 Recommendations: {recs}")
        
        random_recs = recommender.recommend_random(top_k=2)
        self.assertEqual(len(random_recs), 2)
        print(f"  - Random Recs: {random_recs}")

    def test_phase_3_emotion_inference(self):
        print("\n[Phase 3] Testing Emotion Inference...")
        dummy_input = "mock_image_bytes"
        emotion = infer_emotion(dummy_input)
        
        self.assertIn("valence", emotion)
        self.assertIn("arousal", emotion)
        self.assertIn("label", emotion)
        print(f"  - Inferred Emotion: {emotion}")

    def test_phase_4_user_state(self):
        print("\n[Phase 4] Testing User State Construction...")
        # Setup context
        ctx = ContextFeatures(
            time_of_day="night", 
            device_type="mobile",
            location="home"
        )
        
        # Test existing user
        state = get_user_state("u_1", ctx)
        self.assertEqual(state["user_id"], "u_1")
        self.assertIn("profile", state)
        self.assertIn("emotion", state)
        self.assertIn("fatigue", state)
        
        # Check fatigue logic (night time should have penalty)
        self.assertTrue(state["fatigue"]["score"] > 0)
        print(f"  - User State (Night, Mobile): Fatigue Score = {state['fatigue']['score']}")
        
        # Test Vectorization
        vec = to_feature_vector(state)
        self.assertTrue(len(vec) > 0)
        print(f"  - Feature Vector Length: {len(vec)}")
        print(f"  - Feature Vector Sample: {vec[:5]}...")

if __name__ == '__main__':
    unittest.main()
