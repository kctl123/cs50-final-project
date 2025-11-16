#node --> a single point with lat and lon
#way --> collection of nodes, ie restaurants that are in a single building 
#relation --> can group ways/nodes, ie restaurants in food court etc 

import requests, sqlite3, time, json, math, sys, os, re
from typing import Optional
from difflib import SequenceMatcher

DB = os.path.join("..", "data", "copy.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RADIUS_METERS = 75
BATCH_SIZE = 200
SLEEP_BETWEEN_REQUESTS = 2.5

def infer_cuisine_from_name(name: str) -> str:
    name_lower = name.lower()

    multi_word_keywords = {
        "hawker": ["food court", "kopitiam", "canteen", "chicken rice", "mee hoon", "ban mian"],
        "local": ["koufu","kueh", "toast box", "kopi","toastbox", "toast box" "kopi", "teh tarik", "kaya toast", "prata", "chicken rice"],
        "bubble_tea": ["liho","koi","mixue","hitea","chi cha","playmade","cup"]
    }

    single_word_keywords = {
        "japanese": ["ramen", "sushi", "japan", "donburi", "yakitori", "udon", "sashimi", "tempura", "tonkatsu", "teppanyaki","maki", "izakaya", "bento", "matcha", "ramenya", "niku","tokyo","teppei","syokudo","shokudo","japanese"],
        "korean": ["korean", "korea","bibimbap", "kimchi", "bulgogi", "tteokbokki", "soju", "jjigae", "galbi", "samgyeopsal", "hotpot", "seoul", "mandu"],
        "chinese": ["din", "claypot","chinese", "dimsum", "noodle", "dumpling", "wok", "cantonese", "sichuan", "peking", "bao", "springroll", "wonton", "friedrice", "hotpot", "chow", "cuisine","canton"],
        "thai": ["thai", "bangkok", "padthai", "tomyum",  "basil", "mango", "coconut", "lemongrass", "seafood", "spicy"],
        "indian": ["indian", "tandoori", "curry", "masala", "biryani", "naan", "samosa", "tikka", "paneer", "roti", "dal", "chaat", "sizzler", "korma"],
        "italian": ["italian", "pasta", "pizza", "spaghetti", "risotto", "ristorante", "lasagna", "gelato", "penne", "bruschetta", "carbonara", "focaccia", "mozzarella", "parmigiana", "tiramisu"],
        "western": ["cow","steak", "burger", "grill", "bbq", "fries", "ribs", "meat", "club", "smokehouse", "bacon", "chicken", "pizza", "sandwichbar"],
        "malay": ["penyet","geprek","goreng","malay", "nasi", "lemak", "satay", "kampong", "mee", "laksa", "rojak" , "ayam", "rendang", "sambal", "cendol", "goreng"],
        "vietnamese": ["pho", "vietnamese", "banh",  "springroll",   "buncha", "lemongrass", "saigon", "hanoi"],
        "cafe": ["coffee", "cafe", "espresso", "latte", "cappuccino", "mocha", "brew", "bakery", "toast", "smoothie", "waffle", "donut", "tea", "bakery", "brunch","starbucks"],
        "mexican": ["mexican","guzman","stuff'd","taco", "burrito", "quesadilla", "enchilada", "fajita", "nachos", "guacamole","churro", "salsa", "tamale", "carnitas", "jalapeno", "hacienda", "taqueria", "mexico"]
    }


    for cuisine, phrases in multi_word_keywords.items():
        for phrase in phrases:
            if phrase in name_lower:
                return cuisine

    # then check single words using word boundaries
    for cuisine, words in single_word_keywords.items():
        for word in words:
            pattern = r'(?<!\w)' + re.escape(word) + r'(?!\w)'
            if re.search(pattern, name_lower):
                #'\b' is string boundary, re.escape(word) is to ensure special characters get converted to alphabets 
                #if word is standalone will get back \bburgerb and match, but if is not standalone like hamburger will get back diff value and not match
                return cuisine

    for cuisine, words in single_word_keywords.items():
        if any(word in name_lower for word in words):
            return cuisine

    return "unknown" #return unknown if don't have any matches

def overpass_query(lat: float, lon: float, radius: int = (RADIUS_METERS)) -> dict: #takes 3 parameters and returns a dict
    q = f"""
    [out:json][timeout:25]; 
    (
    node(around: {radius}, {lat}, {lon})["amenity"="restaurant"];
    way(around: {radius}, {lat}, {lon})["amenity"="restaurant"];
    relation(around: {radius}, {lat}, {lon})["amenity"="restaurant"];
    );
    out center tags;
    """

    r = requests.post(OVERPASS_URL, data = {"data": q}, timeout = 60) #sends http post request to overpass api, query must be passed under "data" field
    r.raise_for_status() #checks for HTTP errors 
    return r.json()
    
    
#out:json means return in json format, easier for python to parse, timeout:25 means if query takes >25s ignore it
#retrieve 3 objects, node way and relation
#out center tags is a formatting instruction: output directive, geometric center, tags (metadeta like "name", "cuisine" etc)

def overpass_query_dynamic(lat: float, lon: float, base_radius=50, max_radius=200, step=50):
    radius = base_radius
    while radius <= max_radius:
        data = overpass_query(lat, lon, radius)
        elements = data.get("elements", [])
        if elements:
            return data
        radius += step
        print(f"No results at {radius - step}m, increasing radius to {radius}m...")
        time.sleep(1)
    return {"elements": []}


def closest_element(elements: list, lat: float, lon: float, name: str, min_name_ratio: float = 0.65) -> Optional[dict]:
    #overpass returns dicts within a list, Optional[dict] --> return closest match or None
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

        el_name = el.get("tags", {}).get("name", "")
        ratio = SequenceMatcher(None, name.lower(), el_name.lower()).ratio()
                                         
        if d < best_d and ratio >= min_name_ratio:
            best, best_d = el, d

    return best


def ensure_columns(conn):
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
    if "opening_hours" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN opening_hours TEXT;")
    if "phone_number" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN phone_number TEXT;")
    if "website" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN website TEXT;")
    if "amenities" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN amenities TEXT;")
    if "cuisine_confidence" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN cuisine_confidence TEXT;")
    if "osm_checked" not in cols:
        adds.append("ALTER TABLE restaurants ADD column osm_checked INTEGER DEFAULT 0;")
    if "osm_status" not in cols:
        adds.append("ALTER TABLE restaurants ADD COLUMN osm_status TEXT;")

    for sql in adds:
        try:
            db.execute(sql)
        except sqlite3.OperationalError as e:
            print("Failed to add column:", e) 
    conn.commit()


def enrich_batch(limit = BATCH_SIZE):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    ensure_columns(conn)
    rows = db.execute("""SELECT id, name, latitude, longitude 
                      FROM restaurants
                      WHERE (cuisine is NULL OR cuisine = '')
                      AND latitude is NOT NULL
                      AND longitude is NOT NULL
                      AND (osm_checked is NULL OR osm_checked = 0)
                      AND (osm_status is NULL OR osm_status is 'no_match')
                      LIMIT ?
                      """, (limit,)).fetchall()
    if not rows:
        print("No rows to enrich")
        conn.close()
        return
    
    for row in rows:
        id, name, lat, lon = row["id"], row["name"],row["latitude"],row["longitude"]
        if lat is None or lon is None:
            continue

        try:
            data = overpass_query_dynamic(lat, lon)
        except Exception as e:
            print(f"{[id]} Overpass Error {e}, retrying in 5 seconds" )
            time.sleep(5)
            continue

        elements = data.get("elements", [])
        match = closest_element(elements, lat, lon, name)

        if not match:
            print(f"[{id}] No OSM match found.")

            inferred_cuisine = infer_cuisine_from_name(name)
            cuisine_confidence = "medium" if inferred_cuisine != "unknown" else "low"
            db.execute("""
                UPDATE restaurants
                SET osm_checked = 1,
                    osm_status = 'no_match',
                    cuisine = ?,
                    cuisine_confidence = ?
                WHERE id = ?
                """, (inferred_cuisine, cuisine_confidence, id))
            print(f"[{id}] {name} enriched with inferred cuisine={inferred_cuisine}, cuisine_confidence={cuisine_confidence}")
            conn.commit()
            continue

        if match:
            tags = match.get("tags",{})
            cuisine = tags.get("cuisine")
            if not cuisine or cuisine.strip() == "":
                cuisine = infer_cuisine_from_name(name)
            opening_hours = tags.get("opening_hours")
            phone_number = tags.get("phone")
            website = tags.get("website")
            raw_json = json.dumps(tags, ensure_ascii= False) #save the whole tag dict as JSON
            osm_id = str(match.get("id")) 
            osm_type = match.get("type")

            amenities_list= []
            for field in ["wheelchair", "takeaway", "delivery", "diet:halal"]:
                if tags.get(field) == "yes":
                    amenities_list.append(field)
            amenities = ", ".join(amenities_list)
            prev_raw = db.execute("SELECT raw_properties FROM restaurants WHERE id = ?", (id,)).fetchone()[0] #Gets value of raw_properties
            new_raw = (prev_raw or "") +raw_json
            update_fields = {
                "raw_properties": new_raw,
                "osm_id": osm_id,
                "osm_type": osm_type,
                "osm_status": "matched",
            }

            if cuisine:
                update_fields["cuisine"] = cuisine

            if tags.get("cuisine"):
                update_fields["cuisine_confidence"] = "high"
            elif cuisine and cuisine != "unknown":
                update_fields["cuisine_confidence"] = "medium"
            else:
                update_fields["cuisine_confidence"] = "low"

            if opening_hours:
                update_fields["opening_hours"] = opening_hours
            if phone_number:
                update_fields["phone_number"] = phone_number
            if website:
                update_fields["website"] = website
            if amenities:
                update_fields["amenities"] = amenities

            set_clause = ", ".join(f"{key} = ?" for key in update_fields.keys())
            values = list(update_fields.values()) + [id]

            db.execute(f"UPDATE restaurants SET {set_clause} WHERE id = ?", values)
            db.execute("UPDATE restaurants SET osm_checked = 1 WHERE id = ?", (id,))
            conn.commit()

            confidence = update_fields["cuisine_confidence"]
            print(f"[{id}] {name} enriched with cuisine={cuisine} ({osm_type}/{osm_id}), cuisine_confidence: {confidence}")
            time.sleep(SLEEP_BETWEEN_REQUESTS)
    
    conn.close()
    print("Batch Complete")



if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            batch = int(sys.argv[1])
        except ValueError:
            print("Invalid batch size. Please enter an integer.")
            sys.exit(1)
        enrich_batch(limit=batch)
    else:
        enrich_batch()
