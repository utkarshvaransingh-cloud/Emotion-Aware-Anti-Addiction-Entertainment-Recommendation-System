"""Starter data collector for Phase 2.

Usage examples:
  python scripts/collect_data.py --source csv --input data/sample.csv --out data/raw/sample.parquet

For API-based collectors, set keys in .env and implement the fetch_* functions.
"""
import os
import argparse
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def fetch_from_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def fetch_youtube_placeholder(query: str, max_results: int = 10) -> pd.DataFrame:
    # Placeholder: implement using Google YouTube Data API with API key from .env
    print("YouTube fetcher not implemented. Returning empty DataFrame.")
    return pd.DataFrame()


def save_raw(df: pd.DataFrame, out_path: str):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Saved raw data to {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["csv", "youtube"], default="csv")
    parser.add_argument("--input", help="Input file or query string", required=True)
    parser.add_argument("--out", help="Output path (parquet)", default="data/raw/raw_1.parquet")
    args = parser.parse_args()

    if args.source == "csv":
        df = fetch_from_csv(args.input)
    elif args.source == "youtube":
        df = fetch_youtube_placeholder(args.input)
    else:
        raise SystemExit("Unsupported source")

    # Basic hygiene: ensure timestamp column exists
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.Timestamp.now()

    save_raw(df, args.out)


if __name__ == "__main__":
    main()
