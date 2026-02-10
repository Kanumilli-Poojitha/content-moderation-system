from src.api.rate_limiter import check_and_apply_rate_limit

def test_rate_limit():
    user = "testuser"
    for i in range(5):
        assert check_and_apply_rate_limit(user) == False
    assert check_and_apply_rate_limit(user) == True