import sqlite3
import os

DB_PATH = os.path.join("..", "data","copy.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
db = conn.cursor()


budget_map = {
    "cheap": (0,15),
    "medium": (15,40),
    "expensive": (40, 999)
}


price_map = {
    "japanese": 30,       # ramen 15–20, sets 20–30, sushi higher
    "korean": 22,         # BBQ expensive but many casual places
    "chinese": 25,        # zi char/hawker cheap, restaurants mid
    "thai": 23,           # SG Thai usually mid-range
    "indian": 17,         # prata cheap, restaurants 12–20
    "italian": 28,        # pasta/pizza restaurants mostly mid-high
    "western": 20,        # cafes & casual western
    "malay": 10,           # nasi padang/hawker
    "vietnamese": 22,     # pho & banh mi prices
    "mexican": 23,        # burritos & tacos are mid-priced
    "cafe": 22,           # brunch places
    "local": 8            # singaporean hawker foods
}


cuisine_budget = {}

for cuisine, avg_price in price_map.items():
    for range, (min, max) in budget_map.items():
        if min<= avg_price <= max:
            cuisine_budget[cuisine] = range
            break

#UPDATE restaurants SET price_range = {value} WHERE cuisine = {key}

def normalize(text):
    text = text.lower().strip()
    text = text.replace("/", " ").replace("-", " ")
    return text

def main():
    try:
        db.execute("ALTER TABLE restaurants ADD COLUMN price_range TEXT")
    except sqlite3.OperationalError:
        pass
    
    rows = db.execute("SELECT name, id, cuisine FROM restaurants").fetchall()
    count = 0

    for row in rows:
        name = row["name"]
        cuisine_raw = row["cuisine"]
        restaurant_id = row["id"]

        if cuisine_raw is None:
            continue

        cuisine_clean = normalize(cuisine_raw)
        matched = None

        for key in cuisine_budget:
            if key in cuisine_clean:
                matched = cuisine_budget[key] #get price range 
                break
        
        if not matched:
            continue 

        count += 1

        db.execute("UPDATE restaurants SET price_range = ? WHERE id = ?", (matched, restaurant_id))
        print(f"{name} has been updated with a price range of {matched}")

    print(f"{count} restaurants have been enriched with prices")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()

       




