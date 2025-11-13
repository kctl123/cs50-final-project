import sqlite3
import os
import time
import requests
import sys

DB = os.path.join("..","data","copy.db")
BATCH_SIZE = 100
TIME_BETWEEN_REQUESTS = 1.5

def ensure_columns(conn):
    db = conn.cursor()
    db.execute("PRAGMA table_info(restaurants)")
    cols = [r[1] for r in db.fetchall()]
    if "price_range" not in cols:
        db.execute("ALTER TABLE restaurants ADD COLUMN price_range TEXT;")
        conn.commit()

