import pandas as pd
import random
from typing import List

class BaselineRecommender:
    def __init__(self, items_df: pd.DataFrame):
        self.items_df = items_df
        # Pre-compute popularity rank
        if 'popularity' in items_df.columns:
            self.popular_items = items_df.sort_values(by='popularity', ascending=False)['item_id'].tolist()
        else:
            self.popular_items = items_df['item_id'].tolist()

    def recommend(self, user_id: str, top_k: int = 5) -> List[str]:
        """
        Simple baseline: returns top popular items.
        In a real scenario, this would filter out items already seen by user_id.
        """
        # For simplicity, just return top K popular items
        return self.popular_items[:top_k]

    def recommend_random(self, top_k: int = 5) -> List[str]:
        """
        Returns random items (useful for cold start or exploration).
        """
        all_items = self.items_df['item_id'].tolist()
        return random.sample(all_items, min(top_k, len(all_items)))
