import os
import psycopg
from dotenv import load_dotenv


DB_DSN = os.getenv("DB_DSN")

def get_conn():
    if not DB_DSN:
        raise RuntimeError("DB_DSN is not set")
    conn = psycopg.connect(DB_DSN)
    return conn

def init_db():
    conn = get_conn()
    with open("backend/schema.sql", "r") as f:
        schema = f.read()
    with conn.cursor() as cur:
        cur.execute(schema)
    conn.commit()
    conn.close()