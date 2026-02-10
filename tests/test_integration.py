import requests
import time

BASE_URL = "http://localhost:8000"

def test_full_content_flow():
    payload = {
        "text": "integration test content",
        "userId": "integration_user"
    }

    # Submit content
    response = requests.post(f"{BASE_URL}/api/v1/content/submit", json=payload)
    assert response.status_code == 202

    content_id = response.json()["contentId"]
    assert content_id is not None

    # First status check (should be PENDING or already processed)
    status_response = requests.get(f"{BASE_URL}/api/v1/content/{content_id}/status")
    assert status_response.status_code == 200

    status = status_response.json()["status"]
    assert status in ["PENDING", "APPROVED", "REJECTED"]

    # Wait for processor
    time.sleep(3)

    # Check again
    final_response = requests.get(f"{BASE_URL}/api/v1/content/{content_id}/status")
    assert final_response.status_code == 200

    final_status = final_response.json()["status"]
    assert final_status in ["APPROVED", "REJECTED"]