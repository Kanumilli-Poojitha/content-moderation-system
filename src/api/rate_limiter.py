import time
import os
from typing import Optional

RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", 5))

# Try to use Redis for a distributed token-bucket; fall back to in-memory sliding window
try:
    from .redis_client import redis_client
except Exception:
    try:
        from redis_client import redis_client
    except Exception:
        redis_client = None

# In-memory fallback (per-process)
_local_bucket = {}

_TOKEN_BUCKET_LUA = '''
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last_ts')
local tokens = tonumber(data[1])
local last_ts = tonumber(data[2])
if tokens == nil then tokens = capacity end
if last_ts == nil then last_ts = now end

local delta = math.max(0, now - last_ts)
local new_tokens = math.min(capacity, tokens + delta * refill_rate)
local allowed = 0
if new_tokens >= requested then
  new_tokens = new_tokens - requested
  allowed = 1
end
redis.call('HMSET', key, 'tokens', new_tokens, 'last_ts', now)
redis.call('EXPIRE', key, 3600)
return allowed
'''

def check_and_apply_rate_limit(user_id: str) -> bool:
    """Returns True if rate-limited, False otherwise."""
    # Use Redis-based token bucket when possible for distributed limits
    if redis_client:
        try:
            capacity = RATE_LIMIT
            refill_rate = float(RATE_LIMIT) / 60.0
            now = time.time()
            key = f"rate:{user_id}"
            allowed = redis_client.eval(_TOKEN_BUCKET_LUA, 1, key, capacity, refill_rate, now, 1)
            # allowed == 1 means allowed; return True if rate-limited
            return not (int(allowed) == 1)
        except Exception:
            # On Redis errors, fall back to local limiter
            pass

    # Local sliding-window fallback
    now = time.time()
    window = 60
    if user_id not in _local_bucket:
        _local_bucket[user_id] = []

    _local_bucket[user_id] = [t for t in _local_bucket[user_id] if now - t < window]

    if len(_local_bucket[user_id]) >= RATE_LIMIT:
        return True

    _local_bucket[user_id].append(now)
    return False