import joblib, pandas as pd
m = joblib.load('models/baseline.pkl')
df = pd.read_parquet('data/processed/sample_labeled.parquet')
X, _ = __import__('scripts.train_utils', fromlist=['prepare_features']).prepare_features(df)
preds = m['pipeline'].predict(X)
print('preds sample:', preds[:10])