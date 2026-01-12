from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
import os
# Add project root for imports if not already there
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root not in sys.path:
    sys.path.append(root)

from src.feature_schema import ContextFeatures

class RecommendRequest(BaseModel):
    user_id: str
    context: ContextFeatures
    emotion: Optional[Dict[str, Any]] = None # Optional raw emotion override
    genre_filter: Optional[str] = None # New User Request: Access specific Genres
