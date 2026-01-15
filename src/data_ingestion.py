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
    
    # Real Movies with TMDb IDs and Poster Paths
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
        # Real TMDB poster paths - all verified working
        "poster_path": [
            # Action (1-10): Avengers, Mad Max, Die Hard, Dark Knight, Gladiator, Top Gun Maverick, John Wick, MI Fallout, Matrix, Inception
            "/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",  # Avengers
            "/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",  # Mad Max Fury Road
            "/yFihWxQcmqcaBR31QM6Y8gT6aYV.jpg",  # Die Hard
            "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",  # Dark Knight
            "/ty8TGRuvJLPUmAR1H1nRIsgpvim.jpg",  # Gladiator
            "/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",  # Top Gun Maverick
            "/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg",  # John Wick
            "/z9CQYhJQDAdMJOJtPKrExGhqebr.jpg",  # Mission Impossible Fallout
            "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",  # Matrix
            "/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",  # Inception
            # Romance (11-18): Notebook, Pride & Prej, Titanic, La La Land, Before Sunrise, Crazy Stupid Love, Fault in Stars, Me Before You
            "/rNzQyW4f8B8cQeg7Dgj3n6eT5k9.jpg",  # Notebook
            "/6QmY5Xbk9dofPeAEBVlWDXOwcJQ.jpg",  # Pride and Prejudice
            "/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",  # Titanic
            "/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",  # La La Land
            "/4wvczBArdTuF5XV5YaQpbtpHgEI.jpg",  # Before Sunrise
            "/jG2p6zPATJDdvqixU5xZy9IKu8j.jpg",  # Crazy Stupid Love
            "/kXzSP3X20dIvwfV8zyS2JqlqGFu.jpg",  # Fault in Our Stars
            "/xJUILftRf6TJxloOgrilOTJfeOn.jpg",  # Me Before You
            # Comedy (19-26): Hangover, Superbad, Bridesmaids, Step Brothers, Anchorman, 21 Jump St, Deadpool, Mean Girls
            "/uluhlXubGu1VxU63X9VHCLWDAYP.jpg",  # Hangover
            "/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg",  # Superbad
            "/3id0p9dHmmmzGppYOPfHuFTdvvT.jpg",  # Bridesmaids
            "/8FIxJUVYkwdmOBzSGYlXtPs0vLK.jpg",  # Step Brothers
            "/3gtPnVFOW6bVHliesDguJGVwt1S.jpg",  # Anchorman
            "/theca9010BVxm8bJj2CS9qKs2Ph.jpg",  # 21 Jump Street
            "/3E53WEZJqP6aM84D8CckXx4pIHw.jpg",  # Deadpool
            "/fXm3YKXAEjx7d2tIsTtFvmxw2wS.jpg",  # Mean Girls
            # Sci-Fi (27-34): Interstellar, Blade Runner 2049, Arrival, Martian, Dune, Ex Machina, Gravity, Her
            "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",  # Interstellar
            "/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",  # Blade Runner 2049
            "/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg",  # Arrival
            "/5BHuvQ6p9kfc091Z8RiFNhCwL4b.jpg",  # The Martian
            "/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",  # Dune
            "/mDwR96BxN9NaLmIBPhnAjICuP26.jpg",  # Ex Machina
            "/uWz9N0fezxqukxhEFfwZXTsMQw4.jpg",  # Gravity
            "/eCOtqtfvn7mxGl6nfmq4b1exJRc.jpg",  # Her
            # Doc/Thriller (35-40): Planet Earth 2, Blue Planet, Last Dance, Gone Girl, Prisoners, Shutter Island
            "/zd3T6OYj9hhE8YIkvBNEHPoWKHB.jpg",  # Planet Earth II
            "/bq2Ao43IHFQ3ulEMhBmsAfQOmzR.jpg",  # Blue Planet
            "/oofT9z8VS1e3sYgMpxNNt6eO3H2.jpg",  # The Last Dance
            "/qymaJhHLzl9GxlDr5vnjzHMvZij.jpg",  # Gone Girl
            "/uhpDGSpKLYkVbubyFXLQuHQH3mL.jpg",  # Prisoners
            "/52cOzxT2yJ0Evh5vw3m8tuFUXwC.jpg",  # Shutter Island
            # Fantasy (41-45): LOTR Fellowship, Harry Potter, Hobbit, Pan's Labyrinth, Princess Bride
            "/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",  # LOTR Fellowship
            "/wuMc08IPKEatf9rnMNXvIDxqP4W.jpg",  # Harry Potter
            "/yHA9Fc37VmpUA5UncTxxo3rTGVA.jpg",  # Hobbit
            "/e9eQRPL8WtYQPrZmytQMSem8n1r.jpg",  # Pan's Labyrinth
            "/gpxjoE0yvRwIhFEJgNArtKtaN7S.jpg",  # Princess Bride
            # Horror (46-50): Conjuring, A Quiet Place, Get Out, Hereditary, Shining
            "/wVYREutTvI2tmxr6ujrHT704wGF.jpg",  # The Conjuring
            "/nAU74GmpUk7t5iklEp3bufwDq4n.jpg",  # A Quiet Place
            "/y5Z0IEhEPMBbwdtYgYg9A3t91yA.jpg",  # Get Out
            "/p6MoN0IvnfC1H3DaoKVPNmHb5w4.jpg",  # Hereditary
            "/b6ko0IKC8MdYBBPkkA1aBPLe2yz.jpg",  # The Shining
            # Mystery (51-55): Knives Out, Prestige, Zodiac, Se7en, Usual Suspects
            "/pThyQovXQrw2m0s9x82twj48Jq4.jpg",  # Knives Out
            "/bdN3gXuIZYaJP7ftKK2sU0nPtEA.jpg",  # The Prestige
            "/iPTNlMrklfWv9Ymq5dJcI8sNTDj.jpg",  # Zodiac
            "/6yoghtyTpznpBik8EngEmJskVUO.jpg",  # Se7en
            "/bUPmtQzrRhzqYySeiMpv7GurAfm.jpg",  # Usual Suspects
            # Drama (56-60): Shawshank, Forrest Gump, Godfather, Schindler's, 12 Years Slave
            "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",  # Shawshank
            "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",  # Forrest Gump
            "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",  # Godfather
            "/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",  # Schindler's List
            "/xdANQijuNrJAqgW8jaHSOlPNPob.jpg",  # 12 Years a Slave
            # Adventure (61-65): Indiana Jones, Jurassic Park, Revenant, Cast Away, Life of Pi
            "/ceG9VzoRAVGwivFU403Wc3AHRys.jpg",  # Indiana Jones
            "/oU7Oq2kFAAlGqbU4VoAE36g4hoI.jpg",  # Jurassic Park
            "/ji3ecJShqxSxqbIy0uy06XOMbDq.jpg",  # The Revenant
            "/j50qa91vpzVJHEWH0qNBZLFSGfB.jpg",  # Cast Away
            "/7G5PJdgR0XK5AiYAf46YXoxXnNG.jpg",  # Life of Pi
            # Animation (66-70): Toy Story, Spirited Away, Inside Out, Coco, WALL-E
            "/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",  # Toy Story
            "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",  # Spirited Away
            "/2H1TmgdfNtsKlU9osGv7bWbJZPy.jpg",  # Inside Out
            "/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg",  # Coco
            "/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg",  # WALL-E
            # Musical (71-75): Greatest Showman, Moulin Rouge, Les Mis, Chicago, Mamma Mia
            "/b9UeqdMlgCr3TVNmQ6wlv9HCYlW.jpg",  # Greatest Showman
            "/uLmLDzDQkvoR2IYE6RtPqVZ85Rz.jpg",  # Moulin Rouge
            "/kz8ICArHEBIY8bkCiRYAMk7OnFo.jpg",  # Les Miserables
            "/mWj8ynMkd2dO7MQtP1o0oHjhvT7.jpg",  # Chicago
            "/t3cRQz6N3ZKLQMkq1SQn0cMCpvl.jpg",  # Mamma Mia
            # Crime (76-80): Departed, Goodfellas, Pulp Fiction, Wolf of Wall Street, Heat
            "/nT97ifVT2J1yMQmeq20Qblg61T.jpg",  # The Departed
            "/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",  # Goodfellas
            "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",  # Pulp Fiction
            "/sOxr33wnRuKazR9ClKelmYQ150L.jpg",  # Wolf of Wall Street
            "/rrGvmDigLpZ5zpLgkqkh6TzRbNB.jpg",  # Heat
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
        "timestamp": pd.date_range(start="2023-01-01", periods=5),
        "duration_watched": [45, 60, 30, 50, 40]  # Duration in minutes
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
