import os
import sqlite3

DB_PATH = os.path.join("..","data","copy.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
db = conn.cursor()

try:
    db.execute("ALTER TABLE preferences RENAME TO preferences_old")
    print("renamed preferences")

    db.execute("""
            CREATE TABLE preferences(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER,
                region TEXT,
                budget TEXT,
                cuisine TEXT,
                created_at TIMESTAMP DEFAULT (datetime('now','localtime'))
            );
            """)

    print("created new preferences table")

    db.execute("""
            INSERT INTO preferences (user_id, region, budget, cuisine)
            SELECT user_id, region, budget, cuisine FROM preferences_old
            """)

    db.execute("DROP TABLE preferences_old")
    print("dropped old table")

    conn.commit()

except sqlite3.OperationalError as e:
    print(f"Error {e}, rolling back changes")
    conn.rollback()

finally:
    conn.close()
    print("transferred data")

