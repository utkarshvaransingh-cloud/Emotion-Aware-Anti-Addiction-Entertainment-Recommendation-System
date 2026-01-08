import pandas as pd
import numpy as np
from typing import List, Dict

def load_raw_data() -> Dict[str, pd.DataFrame]:
    """
    Mock data loading. In a real scenario, this would load from files or DB.
    """
    # Mock Users
    users_data = {
        "user_id": [f"u_{i}" for i in range(1, 6)],
        "age": [20, 25, 30, 22, 28],
        "interests": ["action,sci-fi", "romance,comedy", "action,thriller", "comedy", "sci-fi,doc"]
    }
    users_df = pd.DataFrame(users_data)
    
    # Mock Items
    items_data = {
        "item_id": [f"i_{i}" for i in range(1, 11)],
        "title": [f"Movie {i}" for i in range(1, 11)],
        "category": ["action", "action", "comedy", "romance", "sci-fi", "sci-fi", "action", "comedy", "thriller", "doc"],
        "duration_minutes": np.random.randint(20, 180, 10),
        "popularity": np.random.rand(10)
    }
    items_df = pd.DataFrame(items_data)
    
    # Mock Interactions
    interactions_data = {
        "user_id": ["u_1", "u_1", "u_2", "u_3", "u_4"],
        "item_id": ["i_1", "i_2", "i_3", "i_1", "i_8"],
        "rating": [5, 4, 5, 3, 4],
        "timestamp": pd.date_range(start="2023-01-01", periods=5)
    }
    interactions_df = pd.DataFrame(interactions_data)
    
    return {
        "users": users_df,
        "items": items_df,
        "interactions": interactions_df
    }

def process_data(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Clean and process data.
    """
    # In this mock, just return as is or do minimal processing
    processed = {}
    for key, df in data_dict.items():
        processed[key] = df.copy()
        # Example: Fill NAs
        # processed[key].fillna(0, inplace=True)
        
    return processed

if __name__ == "__main__":
    raw = load_raw_data()
    processed = process_data(raw)
    print("Data loaded and processed.")
    print("Users:", len(processed["users"]))
    print("Items:", len(processed["items"]))
