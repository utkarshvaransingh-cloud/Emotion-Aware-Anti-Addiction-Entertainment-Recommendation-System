"""Starter data collector for Phase 2.

Usage examples:
  python scripts/collect_data.py --source csv --input data/sample.csv --out data/raw/sample.parquet

For API-based collectors, set keys in .env and implement the fetch_* functions.
"""
import os
import argparse
import base64
import time
import re
from pathlib import Path
try:
    import pandas as pd
except ModuleNotFoundError:
    print("Missing dependency: pandas. Please install dependencies with:\n  python -m pip install -r requirements.txt")
    raise

try:
    import requests
except ModuleNotFoundError:
    print("Missing dependency: requests. Please install dependencies with:\n  python -m pip install -r requirements.txt")
    raise

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def fetch_from_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def _parse_iso8601_duration(dur: str) -> int:
    # Simple parser for YouTube ISO 8601 durations like PT1H2M30S or PT2M10S
    if not isinstance(dur, str):
        return 0
    hours = minutes = seconds = 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
    if m:
        if m.group(1):
            hours = int(m.group(1))
        if m.group(2):
            minutes = int(m.group(2))
        if m.group(3):
            seconds = int(m.group(3))
    return hours * 3600 + minutes * 60 + seconds


def fetch_youtube_api(query: str, max_results: int = 5) -> pd.DataFrame:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY not set in environment (.env)")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
    }
    r = requests.get(search_url, params=params, timeout=20)
    r.raise_for_status()
    items = r.json().get("items", [])
    video_ids = [it["id"]["videoId"] for it in items if it.get("id") and it["id"].get("videoId")]

    if not video_ids:
        return pd.DataFrame()

    params2 = {
        "part": "snippet,contentDetails,statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }
    r2 = requests.get(videos_url, params=params2, timeout=20)
    r2.raise_for_status()
    vids = r2.json().get("items", [])

    rows = []
    for v in vids:
        vid = v.get("id")
        sn = v.get("snippet", {})
        cd = v.get("contentDetails", {})
        stats = v.get("statistics", {})
        duration = _parse_iso8601_duration(cd.get("duration", ""))
        rows.append({
            "content_id": vid,
            "title": sn.get("title"),
            "provider": "youtube",
            "content_type": "video",
            "duration_seconds": duration,
            "published_at": sn.get("publishedAt"),
            "timestamp": pd.Timestamp.now(),
            "event_type": "search_result",
            "watch_time_seconds": None,
            "percent_watched": None,
            "rewatch_count": None,
        })

    return pd.DataFrame(rows)


def fetch_spotify_api(query: str, max_results: int = 5) -> pd.DataFrame:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET not set in environment (.env)")

    token_url = "https://accounts.spotify.com/api/token"
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    data = {"grant_type": "client_credentials"}
    r = requests.post(token_url, headers=headers, data=data, timeout=10)
    r.raise_for_status()
    token = r.json().get("access_token")

    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": max_results}
    r2 = requests.get(search_url, headers=headers, params=params, timeout=20)
    r2.raise_for_status()
    tracks = r2.json().get("tracks", {}).get("items", [])

    rows = []
    for t in tracks:
        rows.append({
            "content_id": t.get("id"),
            "title": t.get("name"),
            "provider": "spotify",
            "content_type": "audio",
            "duration_seconds": (t.get("duration_ms") or 0) // 1000,
            "published_at": (t.get("album", {}).get("release_date")),
            "timestamp": pd.Timestamp.now(),
            "event_type": "search_result",
            "watch_time_seconds": None,
            "percent_watched": None,
            "rewatch_count": None,
        })

    return pd.DataFrame(rows)


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
        df = fetch_youtube_api(args.input, max_results=10)
    elif args.source == "spotify":
        df = fetch_spotify_api(args.input, max_results=10)
    else:
        raise SystemExit("Unsupported source")

    # Basic hygiene: ensure timestamp column exists
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.Timestamp.now()

    save_raw(df, args.out)


if __name__ == "__main__":
    main()
