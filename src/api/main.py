from fastapi import FastAPI, HTTPException
from uuid import uuid4
from models import ContentRequest
from db import get_cursor
from rate_limiter import check_and_apply_rate_limit
from redis_client import publish_event

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/content/submit", status_code=202)
def submit_content(data: ContentRequest):
    if not data.text or not data.userId:
        raise HTTPException(status_code=400, detail="Invalid input")

    if check_and_apply_rate_limit(data.userId):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    content_id = str(uuid4())
    cur = get_cursor()

    cur.execute(
        "INSERT INTO content (id, user_id, text) VALUES (%s,%s,%s)",
        (content_id, data.userId, data.text)
    )
    cur.execute(
        "INSERT INTO moderation_results (content_id, status) VALUES (%s,%s)",
        (content_id, "PENDING")
    )

    event = {"contentId": content_id, "text": data.text, "userId": data.userId}
    publish_event(event)

    return {"contentId": content_id}

@app.get("/api/v1/content/{content_id}/status")
def get_status(content_id: str):
    cur = get_cursor()
    cur.execute(
        "SELECT status FROM moderation_results WHERE content_id=%s",
        (content_id,)
    )
    row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    return {"contentId": content_id, "status": row[0]}