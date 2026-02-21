import requests
import time

BASE_URL = "http://localhost:8000"

def test_full_content_flow():
    payload = {
        "text": "integration test content",
        "userId": "integration_user"
    }

    # Submit content and assert exact response payload shape
    response = requests.post(f"{BASE_URL}/api/v1/content/submit", json=payload)
    assert response.status_code == 202

    json_body = response.json()
    assert isinstance(json_body, dict)
    assert set(json_body.keys()) == {"contentId"}

    content_id = json_body["contentId"]
    assert content_id is not None

    # First status check: assert payload shape and status value
    status_response = requests.get(f"{BASE_URL}/api/v1/content/{content_id}/status")
    assert status_response.status_code == 200

    status_body = status_response.json()
    assert isinstance(status_body, dict)
    assert set(status_body.keys()) == {"contentId", "status"}
    assert status_body["contentId"] == content_id
    assert status_body["status"] in ["PENDING", "APPROVED", "REJECTED"]

    # Poll for processor to update status (up to 15 seconds)
    # Processor may take time to subscribe and process in CI
    max_wait = 15
    start = time.time()
    final_status = "PENDING"
    while time.time() - start < max_wait:
        final_response = requests.get(f"{BASE_URL}/api/v1/content/{content_id}/status")
        assert final_response.status_code == 200

        final_body = final_response.json()
        assert isinstance(final_body, dict)
        assert set(final_body.keys()) == {"contentId", "status"}
        assert final_body["contentId"] == content_id
        final_status = final_body["status"]

        if final_status in ["APPROVED", "REJECTED"]:
            break
        time.sleep(1)

    assert final_status in ["APPROVED", "REJECTED"], f"Status is still {final_status} after {max_wait}s"