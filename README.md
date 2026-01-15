# Emotion-Aware, Anti-Addiction Entertainment Recommendation System

A comprehensive recommendation system that personalizes entertainment content based on user preferences, emotional state, and time of day, while actively preventing overuse and fatigue through anti-addiction features.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                          │
│         ┌──────────┐  ┌───────────┐  ┌────────────┐         │
│         │  Login   │  │ Dashboard │  │ Watch Page │         │
│         └────┬─────┘  └─────┬─────┘  └──────┬─────┘         │
└──────────────┼──────────────┼───────────────┼───────────────┘
               │              │               │
               ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                      │
│    ┌────────────┐    ┌─────────────┐    ┌────────────┐      │
│    │    Auth    │    │  Recommend  │    │  Log Watch │      │
│    └────────────┘    └──────┬──────┘    └────────────┘      │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   RECOMMENDATION ENGINE                      │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐      │
│  │   Emotion    │  │ Anti-Addiction│  │   Ranker     │      │
│  │   Analyzer   │  │    Module     │  │  Algorithm   │      │
│  └──────────────┘  └───────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│         ┌──────────────┐        ┌──────────────┐            │
│         │    Users     │        │ Movies (TMDB)│            │
│         └──────────────┘        └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### 🎭 Mood-Based Recommendations
- **Happy**: Boosts Action, Adventure, Comedy, Musical, Animation
- **Sad**: Recommends Comedy, Romance, Animation to cheer you up
- **Bored**: Suggests Thriller, Sci-Fi, Mystery, Horror for excitement
- **Anxious**: Promotes calming content like Documentary, Animation, Romance
- **Neutral**: Balanced mix of popular genres

### ⏰ Time-of-Day Awareness
- **Morning**: Lighter content (Documentaries, Animation)
- **Afternoon**: Comedy, Romance
- **Evening**: Balanced recommendations
- **Night**: Thriller, Horror, Mystery (with fatigue monitoring)

### 🧘 Anti-Addiction Module
- Real-time fatigue tracking based on session duration
- Soft break reminders at 60+ minutes
- Hard break enforcement at 120+ minutes
- Diversity encouragement to prevent repetitive content

### 🔐 User Authentication
- Login/Signup pages with premium dark theme
- User session management
- Personalized recommendations per user

### 🎬 Real Movie Posters
- 80 real movies with TMDB poster integration
- High-quality movie artwork display

## Project Structure
```
├── backend/          # FastAPI backend service
│   ├── app.py        # Main API with auth & recommendations
│   └── schemas/      # Request/response models
├── frontend/         # Web dashboard
│   ├── index.html    # Main recommendation dashboard
│   ├── login.html    # User login page
│   ├── signup.html   # User registration
│   └── watch.html    # Movie viewing page
├── src/              # Core recommendation logic
│   ├── api/          # API endpoints
│   ├── anti_addiction.py  # Fatigue & intervention logic
│   ├── data_ingestion.py  # Movie data with TMDB posters
│   ├── recommender/  # Ranking algorithms
│   └── emotion/      # Emotion inference
├── data/             # Datasets & user data
├── models/           # Serialized ML models
└── tests/            # Automated tests
```

## Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv .env312
.env312\Scripts\activate  # Windows
# or: source .env312/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Backend Server
```bash
start_api.bat
# Or manually: python backend/app.py
```
Wait for: `SUCCESS: Recommendation Engine Ready`

### 4. Open Frontend
Navigate to `frontend/login.html` in your browser, or run:
```bash
open_frontend.bat
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/login` | POST | User authentication |
| `/auth/register` | POST | User registration |
| `/recommend` | POST | Get personalized recommendations |
| `/log_interaction` | POST | Log user watch history |

## Technologies
- **Backend**: FastAPI, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript
- **ML**: Scikit-learn, Pandas, NumPy
- **Posters**: TMDB API integration
