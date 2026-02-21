import redis
import os
import json
import time
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
MAX_RETRIES = int(os.getenv("REDIS_MAX_RETRIES", 5))
BACKOFF = float(os.getenv("REDIS_RETRY_BACKOFF_SEC", 0.5))

redis_client = None

def _connect():
    global redis_client
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            redis_client.ping()
            logger.info("Connected to Redis")
            return
        except Exception as e:
            logger.warning(f"Redis connect attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                logger.exception("Exceeded Redis connect retries")
                raise
            time.sleep(BACKOFF * (2 ** (attempt - 1)))

_connect()

def publish_event(event):
    try:
        redis_client.publish("content-moderation-events", json.dumps(event))
        logger.debug("Published event to content-moderation-events")
    except Exception:
        logger.exception("Failed to publish event to Redis")