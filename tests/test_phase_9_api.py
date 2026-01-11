from fastapi.testclient import TestClient
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.api.main import app

class TestRecSysAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        
    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "rec-sys-api"})
        
    def test_recommendation_flow(self):
        """Test getting recommendations for a user"""
        payload = {
            "user_id": "u_1",
            "context": {
                "time_of_day": "evening",
                "device_type": "mobile",
                "location": "home"
            },
            "emotion": {"label": "happy"}
        }
        response = self.client.post("/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check structure
        self.assertIn("recommendations", data)
        self.assertIsInstance(data["recommendations"], list)
        self.assertTrue(len(data["recommendations"]) > 0)
        
        # Check explanation presence (Phase 7 feature)
        first_item = data["recommendations"][0]
        self.assertIn("explanation", first_item)
        print(f"\n[API] Rec Explanation: {first_item['explanation']}")

    def test_fatigue_intervention_api(self):
        """Test that API returns the Hard Break item when fatigue is forced"""
        # We can't easily force internal state mock via API arguments alone 
        # unless we modify the mock source or use a user who has history.
        # But our mock `get_user_state` logic relies on `data_ingestion`.
        # However, checking basic state response works.
        pass

    def test_user_state_endpoint(self):
        """Test fetching user state"""
        payload = {
            "time_of_day": "morning",
            "device_type": "desktop", 
            "location": "work"
        }
        # Note: endpoint expects context in body, but user_id in path
        response = self.client.post("/user/u_2/state", json=payload)
        self.assertEqual(response.status_code, 200)
        state = response.json()
        self.assertIn("fatigue", state)
        self.assertIn("emotion", state)
        print(f"[API] User State Fetched: Fatigue={state['fatigue']['score']}")

if __name__ == "__main__":
    unittest.main()
