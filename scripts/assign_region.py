import sqlite3
import os

DB_path = os.path.join("..","data","copy.db")
conn = sqlite3.connect(DB_path)
conn.row_factory = sqlite3.Row
db = conn.cursor()

SG_BOUND = {
    "lat_min": 1.13,
    "lat_max": 1.45,
    "lon_min": 103.69,
    "lon_max": 104.01
}

REGION_BOXES = {
    "North": {"lat_min": 1.35, "lat_max": 1.45, "lon_min": 103.69, "lon_max": 103.90},
    "South": {"lat_min": 1.25, "lat_max": 1.32, "lon_min": 103.80, "lon_max": 103.87},
    "East":  {"lat_min": 1.30, "lat_max": 1.40, "lon_min": 103.90, "lon_max": 104.01},
    "West":  {"lat_min": 1.30, "lat_max": 1.38, "lon_min": 103.69, "lon_max": 103.80},
    "Central": {"lat_min": 1.25, "lat_max": 1.35, "lon_min": 103.75, "lon_max": 103.90}
}

def assign_region(lat,lon):

    for region, bound in REGION_BOXES.items():
        if bound["lat_min"] <= lat <= bound["lat_max"] and bound["lon_min"] <= lon <= bound["lon_max"]:
            return region
        
    if SG_BOUND["lat_min"] <= lat <= SG_BOUND["lat_max"] and SG_BOUND["lon_min"] <= lon <= SG_BOUND["lon_max"]:
        return "Singapore"
    
    return "Unknown"

def main():
    try:
        db.execute("ALTER TABLE restaurants ADD COLUMN region TEXT")
    except sqlite3.OperationalError:
        pass

    rows = db.execute("SELECT id, latitude, longitude FROM restaurants").fetchall()
    for row in rows:    
        id = row["id"]
        lat = row["latitude"]
        lon = row["longitude"]
        region = assign_region(lat, lon)
        db.execute("UPDATE restaurants SET region = ? WHERE id = ?", (region, id))
        conn.commit()
    print("Region assigning complete")
    conn.close()



if __name__ == "__main__":
    main()