import sqlite3
import os

DB = "copy.db"
SEED_PATH = os.path.join("..", "seed.sql")

with sqlite3.connect(DB) as conn:  # auto commits and closes connection
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    with open(SEED_PATH, "r") as f:
        sql_script = f.read()
    
    cursor.executescript(sql_script)

print("success")


# LEARNING POINTS:
# When checking for NULL values, dont use WHERE name = NULL, use WHERE name IS NULL --> NULL is an unknown value that is distinct from empty spaces or 0
# When checking for values, encapsulate values in quotes such as WHERE unit_no = '0' not WHERE unit_no = 0
# DELETE does not return rows, don't use fetchall(), use conn.total_changes to find how many rows are affected
# only conn/cursor objects can execute commands but conn is the whole database. 
# Python creates an implict cursor when we do conn.execute but cannot fetch rows or do operations on it
# Only can commit to connection (makes sense since its the entire database), the cursor CANNOT commit