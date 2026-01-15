from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Emotion-Aware Recommender")


class UserProfile(BaseModel):
    user_id: str
    emotions: List[str] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend")
def recommend(profile: UserProfile):
    # Placeholder response — replace with model-driven recommendations
    return {"user_id": profile.user_id, "recommendations": ["content_1", "content_2"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
