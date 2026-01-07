# Phase 2 — Requirements, data sources, and collection scripts

Goals for Phase 2
- Define data sources and schema suitable for emotion-aware, anti-addiction recommendations.
- Provide data storage layout and a starter data-collection script.
- Document privacy and consent considerations.

Suggested data sources
- Platform APIs (YouTube, Spotify, Netflix-like telemetry) — metadata + engagement signals.
- App instrumentation: session start/stop, play/pause, time-per-content, interaction events.
- Self-reported emotion labels via in-app prompts or short surveys.
- Optional sensor signals (facial expression, device usage) only with explicit consent.

Dataset schema (recommended columns)
- content_id: string — unique id of the content
- title: string
- provider: string — e.g., youtube, spotify
- content_type: string — video/audio/article
- duration_seconds: int
- published_at: timestamp
- user_id: string (hashed/anonymized)
- session_id: string
- timestamp: timestamp — event time
- event_type: string — play, pause, stop, seek, impression, click
- watch_time_seconds: float
- percent_watched: float
- rewatch_count: int
- emotion_label: string — e.g., happy, sad, neutral (source: self-report or inferred)
- mood_score: float — optional continuous emotion score
- addiction_risk_score: float — computed label (optional)
- recommended: bool — whether shown as a recommendation
- recommended_reason: string — tag for explainability

Storage layout
- `data/raw/` — raw ingested files (CSV, JSON, API dumps)
- `data/processed/` — cleaned, joined, and featureified parquet files
- `notebooks/` — EDA and labeling notebooks
- `models/` — trained model artifacts and checkpoints

Privacy & ethics notes
- Always hash or salt `user_id` before storage.
- Store identifiers separately from behavioral logs where possible.
- Obtain explicit consent for emotion/sensor data and document retention policy.

Collector script
- A starter collector is provided at `scripts/collect_data.py`. It supports ingesting local CSVs and placeholders for API-based fetchers. Configure API keys in `.env`.

Next deliverables for Phase 2
- Fill in API-specific collectors (YouTube Data API, Spotify API) with credentials.
- Create sample synthetic dataset and small EDA notebooks.
