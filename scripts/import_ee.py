import sqlite3
import json
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # one level up from /scripts/
DATA_DIR = os.path.join(BASE_DIR, "data")

DB_PATH = os.path.join(DATA_DIR, "restaurants.db")
EATING_PATH = os.path.join(DATA_DIR, "eatingestablishments.geojson")
HAWKER_PATH = os.path.join(DATA_DIR, "hawker_centers.geojson")

# Connect to database
conn = sqlite3.connect(DB_PATH)
db = conn.cursor()

# Load each GeoJSON
with open(EATING_PATH, "r", encoding="utf-8") as f:
    eating_data = json.load(f)

with open(HAWKER_PATH, "r", encoding="utf-8") as f:
    hawker_data = json.load(f)

for feature in eating_data["features"]: #for each restaurant
    props = feature["properties"] #incudes name, address, postal code, type of cuisine
    geom = feature.get("geometry", {}) #includes coordinates
    coords = geom.get("coordinates", [None,None])  # [longitude, latitude]
    description = props.get("Description", "")

    # Clean HTML tags from description
    soup = BeautifulSoup(description, "html.parser")
    attributes = {}

    rows = soup.find_all("tr") #all possible rows for ONE restaurant
    for row in rows: #for each row in that ONE restaurant's description like LIC_NAME, BLK_HOUSE etc
        headers = row.find_all("th")
        cols = row.find_all("td")
        if len(headers) == 1 and len(cols) ==1: #filters out the ATTRIBUTE tr as it has no tds, filters out malformed rows that has 2 tds
            key = headers[0].get_text(strip=True) #strip = TRUE removes leading/trailing whitespace
            value = cols[0].get_text(strip=True)
            attributes[key] = value #assign key-value pairs to attributes dict

    name = attributes.get("BUSINESS_NAME", "N.A")
    license_name = attributes.get("LIC_NAME", "N.A")

    address_parts = [
    attributes.get("BLK_HOUSE", ""),
    attributes.get("STR_NAME", ""),
    attributes.get("UNIT_NO", "")]
    address = " ".join(part for part in address_parts if part).strip() #for part in address_parts, if part is not empty, join with space

    unit_no = attributes.get("UNIT_NO", "N.A")
    level = attributes.get("LEVEL_NO", "N.A")
    postal = attributes.get("POSTCODE", "N.A")
    longitude = coords[0]
    latitude = coords[1]

    db.execute("INSERT INTO restaurants (name, license_name, address, unit_no, level, postal, longitude, latitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
               (name, license_name, address, unit_no, level, postal, longitude, latitude))
    
conn.commit()


print("Imported eating establishments.")

    
        
