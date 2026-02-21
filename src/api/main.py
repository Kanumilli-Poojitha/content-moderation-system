from fastapi import FastAPI, HTTPException
from uuid import uuid4

try:
    from .models import ContentRequest
    from .db import get_cursor
    from .rate_limiter import check_and_apply_rate_limit
    from .redis_client import publish_event
except Exception:
    from models import ContentRequest
    from db import get_cursor
    from rate_limiter import check_and_apply_rate_limit
    from redis_client import publish_event

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("api")

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/content/submit", status_code=202)
def submit_content(data: ContentRequest):
    if not data.text or not data.userId:
        raise HTTPException(status_code=400, detail="Invalid input")

    logger.info(f"Received submission from user={data.userId}")

    if check_and_apply_rate_limit(data.userId):
        logger.info(f"Rate limit exceeded for user={data.userId}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    content_id = str(uuid4())
    try:
        cur = get_cursor()
        cur.execute(
            "INSERT INTO content (id, user_id, text) VALUES (%s,%s,%s)",
            (content_id, data.userId, data.text)
        )
        cur.execute(
            "INSERT INTO moderation_results (content_id, status) VALUES (%s,%s)",
            (content_id, "PENDING")
        )
    except Exception:
        logger.exception("Database error while storing content")
        raise HTTPException(status_code=500, detail="Internal server error")

    event = {"contentId": content_id, "text": data.text, "userId": data.userId}
    try:
        publish_event(event)
    except Exception:
        logger.exception("Failed to publish content submitted event")

    logger.info(f"Accepted content {content_id} for moderation (user={data.userId})")
    return {"contentId": content_id}

@app.get("/api/v1/content/{content_id}/status")
def get_status(content_id: str):
    from uuid import UUID

    try:
        UUID(content_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Content not found")

    cur = get_cursor()
    cur.execute(
        "SELECT status FROM moderation_results WHERE content_id=%s",
        (content_id,)
    )
    row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"contentId": content_id, "status": row[0]}