"""
ML Model Training Script
Trains preference learning model on MovieLens dataset with 80-20 split.
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from collections import defaultdict, Counter
from sklearn.metrics import mean_squared_error
import json

def load_data():
    """Load train and test datasets."""
    data_dir = Path(__file__).parent.parent / "data" / "movielens"
    
    train = pd.read_csv(data_dir / "train.csv")
    test = pd.read_csv(data_dir / "test.csv")
    
    return train, test

def train_genre_preferences(train_df):
    """
    Train genre preference model from ratings.
    Returns learned genre affinities per user.
    """
    print("\n🧠 Training genre preference model...")
    
    # Calculate user-genre preferences
    user_genre_prefs = {}
    
    for user_id in train_df['user_id'].unique():
        user_data = train_df[train_df['user_id'] == user_id]
        
        # Calculate average rating per genre
        genre_ratings = user_data.groupby('primary_genre')['rating'].agg(['mean', 'count'])
        
        # Normalize to 0-1 scale (ratings are 1-5)
        genre_ratings['normalized'] = (genre_ratings['mean'] - 1) / 4.0
        
        # Filter genres with at least 2 ratings
        genre_ratings = genre_ratings[genre_ratings['count'] >= 2]
        
        user_genre_prefs[user_id] = genre_ratings['normalized'].to_dict()
    
    print(f"  ✅ Learned preferences for {len(user_genre_prefs)} users")
    
    # Global genre preferences
    global_genre_prefs = train_df.groupby('primary_genre')['rating'].mean()
    global_genre_prefs = ((global_genre_prefs - 1) / 4.0).to_dict()
    
    return {
        'user_preferences': user_genre_prefs,
        'global_preferences': global_genre_prefs
    }

def calculate_collaborative_filtering(train_df):
    """
    Build user-user similarity for collaborative filtering.
    """
    print("\n🤝 Building collaborative filtering model...")
    
    # Create user-item matrix
    user_item_matrix = train_df.pivot_table(
        index='user_id',
        columns='movie_id',
        values='rating'
    ).fillna(0)
    
    # Calculate user similarities (simplified - use top 50 similar users)
    from scipy.spatial.distance import cosine
    
    user_similarities = {}
    users = user_item_matrix.index.tolist()
    
    print(f"  Calculating similarities for {len(users)} users...")
    
    for i, user in enumerate(users[:100]):  # Limit to first 100 users for speed
        similarities = []
        user_vec = user_item_matrix.loc[user].values
        
        for other_user in users:
            if other_user != user:
                other_vec = user_item_matrix.loc[other_user].values
                
                # Calculate cosine similarity
                if np.sum(user_vec) > 0 and np.sum(other_vec) > 0:
                    sim = 1 - cosine(user_vec, other_vec)
                    similarities.append((other_user, sim))
        
        # Keep top 10 most similar users
        similarities.sort(key=lambda x: x[1], reverse=True)
        user_similarities[user] = similarities[:10]
    
    print(f"  ✅ Built similarity matrix")
    
    return user_similarities

def evaluate_model(model, test_df):
    """
    Evaluate model performance on test set.
    """
    print("\n📊 Evaluating model on test set...")
    
    predictions = []
    actuals = []
    
    user_prefs = model['user_preferences']
    global_prefs = model['global_preferences']
    
    for _, row in test_df.iterrows():
        user_id = row['user_id']
        genre = row['primary_genre']
        actual_rating = row['rating']
        
        # Predict rating based on learned preferences
        if user_id in user_prefs and genre in user_prefs[user_id]:
            pref_score = user_prefs[user_id][genre]
        elif genre in global_prefs:
            pref_score = global_prefs[genre]
        else:
            pref_score = 0.5  # Default
        
        # Convert back to 1-5 scale
        predicted_rating = 1 + (pref_score * 4)
        
        predictions.append(predicted_rating)
        actuals.append(actual_rating)
    
    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    mae = np.mean(np.abs(np.array(predictions) - np.array(actuals)))
    
    print(f"\n  📈 Results:")
    print(f"     RMSE: {rmse:.3f}")
    print(f"     MAE:  {mae:.3f}")
    print(f"     Baseline (random): ~1.12")
    
    return {
        'rmse': rmse,
        'mae': mae,
        'test_size': len(test_df)
    }

def save_model(model, metrics):
    """Save trained model and metrics."""
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save model
    model_path = models_dir / "genre_preferences.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save metrics
    metrics_path = models_dir / "training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n💾 Model saved to: {model_path}")
    print(f"📊 Metrics saved to: {metrics_path}")

if __name__ == "__main__":
    print("="*70)
    print("  ML Model Training Pipeline - MovieLens 100K")
    print("="*70)
    
    # Load data
    print("\n📂 Loading datasets...")
    train_df, test_df = load_data()
    print(f"  Train: {len(train_df)} ratings")
    print(f"  Test:  {len(test_df)} ratings")
    
    # Train model
    model = train_genre_preferences(train_df)
    
    # Collaborative filtering (optional, takes time)
    # user_similarities = calculate_collaborative_filtering(train_df)
    # model['user_similarities'] = user_similarities
    
    # Evaluate
    metrics = evaluate_model(model, test_df)
    
    # Save
    save_model(model, metrics)
    
    print("\n" + "="*70)
    print("✅ Training Complete!")
    print("="*70)
    print(f"\n🎯 Model Performance:")
    print(f"   RMSE: {metrics['rmse']:.3f} (lower is better)")
    print(f"   The model learned {len(model['user_preferences'])} user profiles")
    print(f"   Ready for integration into recommendation system!")
