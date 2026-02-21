import json
import time
import logging

try:
    from .redis_client import pubsub
    from .db import get_cursor
except Exception:
    from redis_client import pubsub
    from db import get_cursor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("processor")

logger.info("Processor started and listening for events...")

for message in pubsub.listen():
    if message["type"] == "message":
        try:
            data = json.loads(message["data"])
            content_id = data.get("contentId")
            text = data.get("text", "")

            status = "REJECTED" if "badword" in text.lower() else "APPROVED"

            cur = get_cursor()
            cur.execute(
                "UPDATE moderation_results SET status=%s, moderated_at=NOW() WHERE content_id=%s",
                (status, content_id)
            )

            logger.info(f"Processed {content_id} -> {status}")
        except Exception:
            logger.exception("Error processing message")

        time.sleep(1)