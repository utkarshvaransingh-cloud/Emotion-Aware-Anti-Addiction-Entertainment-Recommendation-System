import sys
import os

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    print("Testing imports...")
    from src.feature_schema import ContextFeatures, EmotionFeatures
    from src.state import get_user_state
    from src.recommender.final_ranker import FinalRanker
    from src.data_ingestion import load_raw_data
    from backend.schemas.recommend import RecommendRequest
    print("Imports successful!")

    print("Initializing Ranker...")
    ranker = FinalRanker()
    print("Ranker initialized!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
