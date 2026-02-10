import time
from src.api.rate_limiter import check_and_apply_rate_limit

def test_rate_limit_exceeded():
    user = "test_user"

    # Allow first 5 requests
    for _ in range(5):
        assert check_and_apply_rate_limit(user) == False

    # 6th request should be rate limited
    assert check_and_apply_rate_limit(user) == True