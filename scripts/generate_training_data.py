"""
Training Data Generator
Creates synthetic user interaction data with realistic patterns for ML training.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Realistic mood-genre preferences
MOOD_GENRE_PREFERENCES = {
    "happy": {"action": 0.35, "adventure": 0.25, "comedy": 0.20, "animation": 0.10, "musical": 0.10},
    "sad": {"comedy": 0.40, "romance": 0.30, "animation": 0.15, "drama": 0.15},
    "anxious": {"doc": 0.35, "animation": 0.30, "romance": 0.20, "comedy": 0.15},
    "bored": {"thriller": 0.30, "sci-fi": 0.25, "mystery": 0.20, "horror": 0.15, "action": 0.10}
}

# Time-based genre preferences
TIME_GENRE_PREFERENCES = {
    "morning": {"doc": 0.35, "animation": 0.25, "comedy": 0.20, "romance": 0.20},
    "afternoon": {"comedy": 0.30, "romance": 0.25, "action": 0.25, "adventure": 0.20},
    "evening": {"action": 0.25, "thriller": 0.20, "sci-fi": 0.20, "drama": 0.20, "mystery": 0.15},
    "night": {"thriller": 0.30, "horror": 0.25, "mystery": 0.20, "sci-fi": 0.15, "drama": 0.10}
}

# Genre to movie ID mapping (based on our data structure)
GENRE_TO_IDS = {
    "action": list(range(1, 11)),
    "romance": list(range(11, 19)),
    "comedy": list(range(19, 27)),
    "sci-fi": list(range(27, 35)),
    "doc": list(range(35, 38)),
    "thriller": list(range(38, 41)),
    "fantasy": list(range(41, 46)),
    "horror": list(range(46, 51)),
    "mystery": list(range(51, 56)),
    "drama": list(range(56, 61)),
    "adventure": list(range(61, 66)),
    "animation": list(range(66, 71)),
    "musical": list(range(71, 76)),
    "crime": list(range(76, 81))
}

# Movie titles (from our real dataset)
MOVIE_TITLES = {
    1: "The Avengers", 5: "Gladiator", 10: "Inception",
    11: "The Notebook", 15: "Before Sunrise",
    19: "The Hangover", 22: "Step Brothers", 25: "Deadpool",
    27: "Interstellar", 30: "The Martian", 32: "Dune",
    35: "Planet Earth II", 36: "Blue Planet",
    38: "Gone Girl", 40: "Shutter Island",
    46: "The Conjuring", 48: "Get Out",
    51: "Knives Out", 53: "Zodiac",
    56: "The Shawshank Redemption", 58: "The Godfather",
    66: "Toy Story", 68: "Inside Out", 70: "WALL-E",
    71: "The Greatest Showman", 73: "Les Misérables"
}

def generate_training_data(num_users=5, interactions_per_user=30):
    """
    Generate realistic training data with mood-time-genre correlations.
    """
    interactions = []
    start_date = datetime.now() - timedelta(days=90)  # 3 months of history
    
    for user_num in range(1, num_users + 1):
        user_id = f"u_{user_num}"
        
        # Each user has preferred moods and times
        preferred_mood = random.choice(list(MOOD_GENRE_PREFERENCES.keys()))
        preferred_time = random.choice(list(TIME_GENRE_PREFERENCES.keys()))
        
        for _ in range(interactions_per_user):
            # Choose mood (70% preferred, 30% random)
            if random.random() < 0.7:
                mood = preferred_mood
            else:
                mood = random.choice(list(MOOD_GENRE_PREFERENCES.keys()))
            
            # Choose time (60% preferred, 40% realistic distribution)
            if random.random() < 0.6:
                time_of_day = preferred_time
            else:
                time_of_day = random.choice(list(TIME_GENRE_PREFERENCES.keys()))
            
            # Select genre based on mood and time combination
            mood_prefs = MOOD_GENRE_PREFERENCES[mood]
            time_prefs = TIME_GENRE_PREFERENCES[time_of_day]
            
            # Combine preferences
            combined_prefs = {}
            all_genres = set(mood_prefs.keys()) | set(time_prefs.keys())
            for genre in all_genres:
                combined_prefs[genre] = mood_prefs.get(genre, 0) + time_prefs.get(genre, 0)
            
            # Normalize
            total = sum(combined_prefs.values())
            combined_prefs = {k: v/total for k, v in combined_prefs.items()}
            
            # Sample genre
            genre = random.choices(
                list(combined_prefs.keys()),
                weights=list(combined_prefs.values()),
                k=1
            )[0]
            
            # Sample movie from genre
            movie_num = random.choice(GENRE_TO_IDS.get(genre, [1]))
            movie_id = f"i_{movie_num}"
            movie_title = MOVIE_TITLES.get(movie_num, f"Movie {movie_num}")
            
            # Duration (realistic)
            movie_duration = random.randint(90, 180)
            
            # Watch duration and completion
            # Higher completion for preferred mood+time combinations
            base_completion_prob = 0.5
            if mood == preferred_mood:
                base_completion_prob += 0.2
            if time_of_day == preferred_time:
                base_completion_prob += 0.2
            
            if random.random() < base_completion_prob:
                # Completed
                duration_watched = movie_duration
                completed = True
            else:
                # Partial watch
                duration_watched = random.randint(10, movie_duration - 10)
                completed = False
            
            # Timestamp
            timestamp = start_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            interaction = {
                "user_id": user_id,
                "movie_id": movie_id,
                "title": movie_title,
                "emotion": mood,
                "time_of_day": time_of_day,
                "duration_watched": duration_watched,
                "movie_duration": movie_duration,
                "completed": completed,
                "timestamp": timestamp.isoformat() + "Z"
            }
            
            interactions.append(interaction)
    
    return interactions

if __name__ == "__main__":
    # Generate training data
    print("Generating synthetic training dataset...")
    training_data = generate_training_data(num_users=5, interactions_per_user=30)
    
    # Save to file
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    output_file = data_dir / "interactions.json"
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"✅ Generated {len(training_data)} interactions")
    print(f"📁 Saved to: {output_file}")
    print("\nDataset Statistics:")
    
    # Print stats
    users = set(i["user_id"] for i in training_data)
    moods = {}
    times = {}
    for i in training_data:
        moods[i["emotion"]] = moods.get(i["emotion"], 0) + 1
        times[i["time_of_day"]] = times.get(i["time_of_day"], 0) + 1
    
    print(f"  Users: {len(users)}")
    print(f"  Moods: {moods}")
    print(f"  Times: {times}")
    print(f"  Completion rate: {sum(1 for i in training_data if i['completed']) / len(training_data) * 100:.1f}%")
