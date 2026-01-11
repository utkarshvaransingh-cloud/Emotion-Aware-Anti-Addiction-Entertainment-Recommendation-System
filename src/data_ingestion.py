import pandas as pd
import numpy as np
from typing import List, Dict

def load_raw_data() -> Dict[str, pd.DataFrame]:
    """
    Real movie data with TMDb poster paths.
    """
    # Mock Users
    users_data = {
        "user_id": [f"u_{i}" for i in range(1, 6)],
        "age": [20, 25, 30, 22, 28],
        "interests": ["action,sci-fi", "romance,comedy", "action,thriller", "comedy", "sci-fi,doc"]
    }
    users_df = pd.DataFrame(users_data)
    
    # Real Movies with TMDb Poster IDs
    items_data = {
        "item_id": [f"i_{i}" for i in range(1, 81)],
        "title": [
            # Action (1-10)
            "The Avengers", "Mad Max: Fury Road", "Die Hard", "The Dark Knight", "Gladiator",
            "Top Gun: Maverick", "John Wick", "Mission: Impossible", "The Matrix", "Inception",
            # Romance (11-18)
            "The Notebook", "Pride and Prejudice", "Titanic", "La La Land", "Before Sunrise",
            "Crazy, Stupid, Love", "The Fault in Our Stars", "Me Before You",
            # Comedy (19-26)
            "The Hangover", "Superbad", "Bridesmaids", "Step Brothers", "Anchorman",
            "21 Jump Street", "Deadpool", "Mean Girls",
            # Sci-Fi (27-34)
            "Interstellar", "Blade Runner 2049", "Arrival", "The Martian", "Dune",
            "Ex Machina", "Gravity", "Her",
            # Documentaries & Thrillers (35-40)
            "Planet Earth II", "Blue Planet", "The Last Dance", "Gone Girl", "Prisoners", "Shutter Island",
            # Fantasy (41-45)
            "The Lord of the Rings", "Harry Potter", "The Hobbit", "Pan's Labyrinth", "The Princess Bride",
            # Horror (46-50)
            "The Conjuring", "A Quiet Place", "Get Out", "Hereditary", "The Shining",
            # Mystery (51-55)
            "Knives Out", "The Prestige", "Zodiac", "Seven", "The Usual Suspects",
            # Drama (56-60)
            "The Shawshank Redemption", "Forrest Gump", "The Godfather", "Schindler's List", "12 Years a Slave",
            # Adventure (61-65)
            "Indiana Jones", "Jurassic Park", "The Revenant", "Cast Away", "Life of Pi",
            # Animation (66-70)
            "Toy Story", "Spirited Away", "Inside Out", "Coco", "WALL-E",
            # Musical (71-75)
            "The Greatest Showman", "Moulin Rouge", "Les Misérables", "Chicago", "Mamma Mia!",
            # Crime (76-80)
            "The Departed", "Goodfellas", "Pulp Fiction", "The Wolf of Wall Street", "Heat"
        ],
        "tmdb_id": [
            # Action
            24428, 76341, 562, 155, 98,
            361743, 245891, 137113, 603, 27205,
            # Romance
            11036, 131, 597, 313369, 3082,
            117251, 222935, 296098,
            # Comedy
            18785, 8363, 55931, 12133, 8699,
            245891, 293660, 27578,
            # Sci-Fi
            157336, 335984, 329865, 286217, 438631,
            264660, 109445, 152601,
            # Doc/Thriller
            417279, 417280, 587693, 550, 395834, 11324,
            # Fantasy
            120, 671, 49051, 1327, 2493,
            # Horror
            138843, 447332, 419430, 493922, 694,
            # Mystery
            546554, 1124, 185, 807, 629,
            # Drama
            278, 13, 238, 424, 382322,
            # Adventure
            85, 329, 281957, 8358, 87827,
            # Animation
            862, 129, 150540, 354912, 10681,
            # Musical
            316029, 824, 25188, 113, 123,
            # Crime  
            56, 769, 680, 106646, 949
        ],
        "category": [
            "action"]*10 + ["romance"]*8 + ["comedy"]*8 + ["sci-fi"]*8 + ["doc"]*3 + ["thriller"]*3 +
            ["fantasy"]*5 + ["horror"]*5 + ["mystery"]*5 + ["drama"]*5 + ["adventure"]*5 + 
            ["animation"]*5 + ["musical"]*5 + ["crime"]*5,
        "duration_minutes": np.random.randint(90, 180, 80),
        "popularity": np.random.uniform(0.1, 0.99, 80)
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
    processed = {}
    for key, df in data_dict.items():
        processed[key] = df.copy()
        
    return processed

if __name__ == "__main__":
    raw = load_raw_data()
    processed = process_data(raw)
    print("Data loaded and processed.")
    print("Users:", len(processed["users"]))
    print("Items:", len(processed["items"]))
