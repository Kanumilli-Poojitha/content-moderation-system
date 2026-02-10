import json
import random
import time
from redis_client import pubsub
from db import get_cursor

print("Processor started...")

for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        content_id = data["contentId"]
        text = data["text"]

        status = "REJECTED" if "badword" in text.lower() else "APPROVED"

        cur = get_cursor()
        cur.execute(
            "UPDATE moderation_results SET status=%s, moderated_at=NOW() WHERE content_id=%s",
            (status, content_id)
        )

        print(f"Processed {content_id} -> {status}")
        time.sleep(1)