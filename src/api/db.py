import psycopg2
import os
import time
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", 5))
BACKOFF = float(os.getenv("DB_RETRY_BACKOFF_SEC", 1.0))

_conn = None

def _connect():
    global _conn
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _conn = psycopg2.connect(DATABASE_URL)
            _conn.autocommit = True
            logger.info("Connected to Postgres database")
            return
        except Exception as e:
            logger.warning(f"Postgres connect attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                logger.exception("Exceeded Postgres connect retries")
                raise
            time.sleep(BACKOFF * (2 ** (attempt - 1)))

_connect()

def get_cursor():
    global _conn
    try:
        return _conn.cursor()
    except Exception:
        logger.exception("Lost DB connection, attempting reconnect")
        _connect()
        return _conn.cursor()