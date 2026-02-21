import os
import time
import json
import importlib
import pytest

import redis


def test_redis_pubsub_integration():
    """Integration test that validates API publish -> Redis channel -> subscriber receives message.

    Requires a Redis instance running and reachable via REDIS_URL (default redis://localhost:6379).
    """
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

    # Check Redis availability first; skip test if not reachable
    try:
        r_check = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
        r_check.ping()
    except Exception:
        pytest.skip("Redis not available at REDIS_URL; skipping integration test")

    # Reload the API redis_client module so it uses the test REDIS_URL
    try:
        import src.api.redis_client as api_redis
        importlib.reload(api_redis)
    except Exception:
        # If package import fails, try top-level import (legacy)
        import redis_client as api_redis
        importlib.reload(api_redis)

    r = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe("content-moderation-events")

    # Give subscription a moment to register
    time.sleep(0.1)

    event = {"contentId": "integration-test-id", "text": "hello world", "userId": "tester"}

    # Publish via the API's publish_event helper
    api_redis.publish_event(event)

    # Wait for message up to a few seconds
    timeout = 5
    end = time.time() + timeout
    received = None
    while time.time() < end:
        message = pubsub.get_message(timeout=1)
        if message and message.get("type") == "message":
            received = message
            break
        time.sleep(0.05)

    assert received is not None, "Did not receive any message from Redis channel"
    data = json.loads(received["data"]) if isinstance(received["data"], str) else received["data"]
    assert data == event
