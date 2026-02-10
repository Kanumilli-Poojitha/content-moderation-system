import redis
import os
import json

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def publish_event(event):
    redis_client.publish("content-moderation-events", json.dumps(event))