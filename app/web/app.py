from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

from common.db import get_conn

app = FastAPI()

RETRIEVAL_URL = "http://retrieval:8000/fetch"
ANALYSIS_URL = "http://analysis:8000/analyze"


# -------- Request schema --------

class TopicRequest(BaseModel):
    topic: str


# -------- Helper --------

def get_topics() -> list[str]:
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT topic
                FROM articles
                WHERE topic IS NOT NULL AND topic != ''
                ORDER BY topic
            """)
            rows = cursor.fetchall()
        return [row[0] for row in rows]


# -------- Routes --------

@app.get("/topics")
def topics():
    return {"topics": get_topics()}


@app.post("/fetch")
def fetch(req: TopicRequest):
    topic = req.topic.strip().lower()
    if not topic:
        raise HTTPException(status_code=400, detail="No topic provided")

    r = requests.post(RETRIEVAL_URL, json={"topic": topic})
    return {"message": r.text}


@app.post("/analyze")
def analyze(req: TopicRequest):
    topic = req.topic.strip().lower()
    if not topic:
        raise HTTPException(status_code=400, detail="No topic provided")

    r = requests.post(ANALYSIS_URL, json={"topic": topic})
    r.raise_for_status()
    data = r.json()

    return {"message": data}


@app.post("/delete_topic")
def delete_topic(req: TopicRequest):
    topic = req.topic.strip().lower()
    if not topic:
        raise HTTPException(status_code=400, detail="No topic provided")

    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM articles
                WHERE topic = %s
            """, (topic,))
            deleted_count = cursor.rowcount
        conn.commit()

    return {"message": f"Deleted {deleted_count} articles for topic: {topic}"}


@app.post("/clear_database")
def clear_database():
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM articles")
        conn.commit()

    return {"message": "Deleted all entries in database."}


@app.get("/health")
def health():
    return {"status": "ok"}