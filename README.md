# Emotion-Aware, Anti-Addiction Entertainment Recommendation System

A comprehensive recommendation system that personalizes entertainment content (videos, music, games) based on user preferences and emotional state, while actively preventing overuse and fatigue.

## Project Structure
- `data/`: Datasets (raw, processed)
- `src/`: Source code including feature definitions, data ingestion, recommendation logic, and emotion inference.
- `backend/`: FastAPI backend service.
- `frontend/`: (Future) Web dashboard.
- `models/`: Serialized models.
- `tests/`: Automated tests.

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
