"""
MovieLens Dataset Downloader and Preprocessor
Downloads MovieLens 100K dataset and prepares it for training.
"""
import requests
import zipfile
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import shutil

def download_movielens():
    """Download and extract MovieLens 100K dataset."""
    print("📥 Downloading MovieLens 100K dataset...")
    
    # Create directories
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data" / "movielens"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if zip exists in root
    root_zip = root_dir / "ml-100k.zip"
    zip_path = data_dir / "ml-100k.zip"
    
    if root_zip.exists():
        print(f"📦 Found local dataset at {root_zip}, copying...")
        shutil.copy(root_zip, zip_path)
    else:
        # Download URL
        url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
        
        # Download
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                print(f"\r  Progress: {progress:.1f}%", end='')
        print("\n✅ Download complete!")
    
    # Extract
    print("📂 Extracting files...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    
    print("✅ Extraction complete!")
    return data_dir / "ml-100k"

def preprocess_data(ml_dir):
    """
    Process MovieLens data into usable format.
    Returns train and test DataFrames.
    """
    print("\n🔧 Preprocessing data...")
    
    # Load ratings (u.data: user_id, item_id, rating, timestamp)
    ratings_file = ml_dir / "u.data"
    ratings = pd.read_csv(
        ratings_file, 
        sep='\t', 
        names=['user_id', 'movie_id', 'rating', 'timestamp'],
        engine='python'
    )
    
    # Load movies (u.item: movie_id, title, genres...)
    movies_file = ml_dir / "u.item"
    movies = pd.read_csv(
        movies_file,
        sep='|',
        encoding='latin-1',
        names=['movie_id', 'title', 'release_date', 'video_release_date', 'imdb_url',
               'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy',
               'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
               'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'],
        engine='python'
    )
    
    # Extract primary genre for each movie
    genre_columns = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                     'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
                     'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    
    def get_primary_genre(row):
        for genre in genre_columns:
            if row[genre] == 1:
                return genre.lower()
        return 'unknown'
    
    movies['primary_genre'] = movies.apply(get_primary_genre, axis=1)
    
    # Merge ratings with movie metadata
    data = ratings.merge(movies[['movie_id', 'title', 'primary_genre']], on='movie_id')
    
    print(f"  Total ratings: {len(data)}")
    print(f"  Users: {data['user_id'].nunique()}")
    print(f"  Movies: {data['movie_id'].nunique()}")
    
    # 80-20 Train-Test Split (stratified by user to ensure all users in both sets)
    print("\n🔀 Splitting into train (80%) and test (20%)...")
    train_data, test_data = train_test_split(
        data, 
        test_size=0.2, 
        random_state=42,
        stratify=data['user_id'].apply(lambda x: min(x, 50))  # Stratify on binned user_id
    )
    
    print(f"  Train set: {len(train_data)} ratings")
    print(f"  Test set: {len(test_data)} ratings")
    
    # Save processed data
    output_dir = Path(__file__).parent.parent / "data" / "movielens"
    train_data.to_csv(output_dir / "train.csv", index=False)
    test_data.to_csv(output_dir / "test.csv", index=False)
    movies[['movie_id', 'title', 'primary_genre']].to_csv(output_dir / "movies.csv", index=False)
    
    print(f"\n✅ Saved to {output_dir}/")
    
    return train_data, test_data

if __name__ == "__main__":
    print("="*60)
    print("  MovieLens 100K Dataset Download & Preprocessing")
    print("="*60)
    
    # Download
    ml_dir = download_movielens()
    
    # Preprocess
    train, test = preprocess_data(ml_dir)
    
    print("\n" + "="*60)
    print("✅ Dataset ready for training!")
    print("="*60)
    
    # Show genre distribution
    print("\nGenre Distribution in Training Set:")
    genre_counts = train['primary_genre'].value_counts()
    for genre, count in genre_counts.head(10).items():
        print(f"  {genre}: {count} ratings")
