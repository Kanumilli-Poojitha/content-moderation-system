import psycopg2
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.autocommit = True

def get_cursor():
    return conn.cursor()