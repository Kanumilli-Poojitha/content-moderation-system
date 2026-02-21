import redis
import os
import time
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
MAX_RETRIES = int(os.getenv("REDIS_MAX_RETRIES", 5))
BACKOFF = float(os.getenv("REDIS_RETRY_BACKOFF_SEC", 0.5))

redis_client = None
pubsub = None

def _connect():
	global redis_client, pubsub
	for attempt in range(1, MAX_RETRIES + 1):
		try:
			redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
			redis_client.ping()
			pubsub = redis_client.pubsub()
			pubsub.subscribe("content-moderation-events")
			logger.info("Processor connected to Redis and subscribed to channel")
			return
		except Exception as e:
			logger.warning(f"Processor Redis connect attempt {attempt} failed: {e}")
			if attempt == MAX_RETRIES:
				logger.exception("Processor exceeded Redis connect retries")
				raise
			time.sleep(BACKOFF * (2 ** (attempt - 1)))

_connect()