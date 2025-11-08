import sqlite3
import os

# Get the base directory of the script
BASE_DIR = os.path.dirname(__file__)

# Paths for the database and schema
DB_PATH = os.path.join(BASE_DIR, "data", "restaurants.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# --- Step 1: Delete the old database if it exists ---
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Old database deleted.")

# --- Step 2: Create a new database and connect ---
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print("New database created.")

# --- Step 3: Read schema.sql and execute ---
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)

conn.commit()
conn.close()

print("Database created successfully!")
