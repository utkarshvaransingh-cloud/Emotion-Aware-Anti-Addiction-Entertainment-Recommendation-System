"""Generate a small synthetic sample dataset for Phase 2 demos.

Usage:
  python scripts/generate_sample.py --out data/samples/sample.csv --n 100
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np


def make_sample(n=100):
    rng = np.random.default_rng(42)
    providers = ["youtube", "spotify"]
    content_types = {"youtube": "video", "spotify": "audio"}

    rows = []
    for i in range(n):
        provider = rng.choice(providers)
        cid = f"{provider[:3]}_{i:04d}"
        duration = int(rng.integers(30, 3600))
        watch = round(rng.uniform(0, duration), 2)
        percent = round((watch / duration) * 100, 2)
        rows.append({
            "content_id": cid,
            "title": f"Sample content {i}",
            "provider": provider,
            "content_type": content_types[provider],
            "duration_seconds": duration,
            "published_at": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 365))),
            "user_id": f"user_{rng.integers(1,10)}",
            "session_id": f"sess_{rng.integers(1,1000)}",
            "timestamp": pd.Timestamp.now(),
            "event_type": rng.choice(["play", "pause", "stop"]),
            "watch_time_seconds": watch,
            "percent_watched": percent,
            "rewatch_count": int(rng.integers(0, 5)),
            "emotion_label": rng.choice(["happy", "sad", "neutral"]),
        })

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/samples/sample.csv")
    parser.add_argument("--n", type=int, default=200)
    args = parser.parse_args()

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    df = make_sample(args.n)
    df.to_csv(outp, index=False)
    print(f"Wrote sample dataset to {outp}")


if __name__ == "__main__":
    main()
