from pathlib import Path
import pandas as pd
import joblib
import numpy as np

processed = Path('data/processed/sample_processed.parquet')
labeled = Path('data/processed/sample_labeled.parquet')

# load available dataframe
if labeled.exists():
    df = pd.read_parquet(labeled)
    src = labeled
elif processed.exists():
    df = pd.read_parquet(processed)
    src = processed
else:
    raise SystemExit('No processed data found')

print(f'Loaded {src} with {len(df)} rows')

# label counts
if 'emotion_label' in df.columns:
    counts = df['emotion_label'].value_counts(dropna=False)
    print('\nLabel counts:')
    print(counts)
    total_labeled = df['emotion_label'].notna().sum()
    try:
        min_count = int(counts.min())
    except Exception:
        min_count = 0
else:
    print('\nNo emotion_label column — 0 labeled')
    counts = pd.Series(dtype=int)
    total_labeled = 0
    min_count = 0

# prepare simple features without importing repo utilities
# fill missing
df2 = df.copy()
df2 = df2.fillna({'duration_seconds':0,'percent_watched':0,'provider':'unknown','content_type':'unknown'})
numeric = df2[['duration_seconds','percent_watched']].astype(float)
cat = pd.get_dummies(df2[['provider','content_type']].astype(str), prefix_sep='=')
X = pd.concat([numeric, cat], axis=1).values
print('\nFeature matrix shape:', X.shape)

# load model if exists
model_path = Path('models/baseline.pkl')
if model_path.exists():
    mdl = joblib.load(model_path)
    # model may be dict
    if isinstance(mdl, dict) and 'pipeline' in mdl:
        pipe = mdl['pipeline']
    else:
        pipe = mdl
    try:
        preds = pipe.predict(X)
        print('\nSample predictions:', list(preds[:10]))
    except Exception as e:
        print('\nModel present but prediction failed:', e)
else:
    print('\nNo model found at models/baseline.pkl')

# decide if more labels needed
need_more = False
reason = []
if total_labeled < 50:
    need_more = True
    reason.append(f'total_labeled={total_labeled}<50')
if min_count < 2:
    need_more = True
    reason.append(f'min_class_count={min_count}<2')

if need_more:
    out = Path('labels')
    out.mkdir(parents=True, exist_ok=True)
    samp = 500 if len(df)>500 else len(df)
    # sample from processed (not labeled) if possible
    proc_df = pd.read_parquet(processed) if processed.exists() else df
    # exclude already labeled content_ids if available
    if 'content_id' in proc_df.columns and 'content_id' in df.columns:
        labeled_ids = set(df['content_id'].dropna().astype(str))
        pool = proc_df[~proc_df['content_id'].astype(str).isin(labeled_ids)]
    else:
        pool = proc_df
    s = pool.sample(min(len(pool), samp), random_state=42)
    sample_path = out / 'sample_for_labeling.csv'
    s.to_csv(sample_path, index=False)
    print(f'\nExported {len(s)} rows to {sample_path} because: {", ".join(reason)}')
else:
    print('\nLabel set seems sufficient for now (heuristic).')
