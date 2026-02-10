import time
import os

RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", 5))
bucket = {}

def check_and_apply_rate_limit(user_id: str) -> bool:
    now = time.time()
    window = 60

    if user_id not in bucket:
        bucket[user_id] = []

    bucket[user_id] = [t for t in bucket[user_id] if now - t < window]

    if len(bucket[user_id]) >= RATE_LIMIT:
        return True

    bucket[user_id].append(now)
    return False