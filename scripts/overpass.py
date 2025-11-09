#node --> a single point with lat and lon
#way --> collection of nodes, ie restaurants that are in a single building 
#relation --> can group ways/nodes, ie restaurants in food court etc 

import requests, sqlite3, time, json, math, sys, os
from typing import Optional

DB = os.path.join("..", "data", "copy.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RADIUS_METERS = 20
BATCH_SIZE = 200
SLEEP_BETWEEN_REQUESTS = 1.5

def overpass_query(lat: float, lon: float, radius: int = (RADIUS_METERS)) -> dict: #takes 3 parameters and returns a dict
    q = f"""
    [out:json][timeout:25]; 
    (
    node(around: {radius}, {lat}, {lon})["amenity" = "restaurant];
    way(around: {radius}, {lat}, {lon})["amenity = "restaurant];
    relation(around: {radius}, {lat}, {lon})["amenity" = "restaurant];
    );
    out center tags;
    """

    r = requests.post(OVERPASS_URL, data = {"data:q "}, timeout = 60) #sends http post request to overpass api, query must be passed under "data" field
    r.raise_for_status #checks for HTTP errors 
    return r.json
    
#out:json means return in json format, easier for python to parse, timeout:25 means if query takes >25s ignore it
#retrieve 3 objects, node way and relation
#out center tags is a formatting instruction: output directive, geometric center, tags (metadeta like "name", "cuisine" etc)

def closest_element(elements: list, lat: float, lon: float) -> Optional[dict]: #overpass returns dicts within a list, Optional[dict] --> return closest match or None
    #picks the closest matching place from a list of Overpass API results given a set of coordinates
    best = None #hold the closest restaurant found      
    best_d = float("inf") #set initial best distance to be infinity then slowly narrow down
    
    for el in elements: #formatting, if it returns a node it will have lat and lon, if it returns a way the lat at lon are stored in a dict called center ie "center" :{"lat" : 123", "lon": 123}
        if "center" in el:
            el_lat = el["center"]["lat"]
            el_lon = el["center"]["lon"]
        elif "lat" in el and "lon" in el:
            el_lat = el["lat"]
            el_lon = el["lon"]
        else:
            continue
    
    #when we enter a given lat and lon into overpass_query, 
    #the list that overpass returns contains multiple nearby places and we are looping through lat and lon of each of the places to find the closest match

    d = (el_lat - lat) ** 2 + (el_lon - lon) ** 2
    if d < best_d:
            best, best_d = el, d
    return best


def ensure_columns():
    conn = sqlite3.connect(DB)
    db = conn.cursor()
    db.execute("PRAGMA table_info(restaurants);") #similar to running .schema on restaurants
    cols = [r[1] for r in db.fetchall()] #r[1] due to format of db.fetchall()

    adds = [] #makes it idempotent so it doesn't crash when column already exists 
    if "cuisine" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN cuisine TEXT;")
    if "raw_properties" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN raw_properties TEXT;")
    if "osm_id" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN osm_id TEXT;")
    if "osm_type" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN osm_type TEXT;")

    for sql in adds:
        try:
            db.execute(sql)
        except sqlite3.OperationalError as e:
            print("Failed to add column:", e) 
    conn.commit()

