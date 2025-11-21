import os
import sqlite3

DB_PATH = os.path.join("..","data","copy.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
db = conn.cursor()

def normalize(text):
    if not text:
        return ""
    text = text.lower().strip()
    replacements = ["&", "/", "-", "(", ")", ".", ","]
    for r in replacements:
        text = text.replace(r, " ")
    text = " ".join(text.split())
    return text

CATEGORY_KEYWORDS = {
    "Hawker": [
        # General indicators
        "hawker", "food centre", "food center", "coffeeshop", "coffee shop",
        "kopitiam", "kopi tiam", "zi char", "zichar", "tze char",
        "kway chap", "economic rice", "mixed rice", "cai fan",
        # Common hawker dish terms
        "chicken rice", "char siew", "roast pork", "duck rice", 
        "bak kut teh", "laksa", "ban mian", "mee hoon kueh",
        "fishball", "fish ball", "hokkien mee", "fried kway teow",
        "carrot cake", "fried carrot cake", "roti prata", "prata",
        "satay", "mee siam", "mee rebus", "nasi padang", "nasi lemak",
        "yong tau foo", "yong tau fu",
    ],

    "Cafe": [
        "cafe", "coffee", "espresso", "cold brew", "latte", "flat white",
        "mocha", "brunch", "all-day breakfast", "toast", "sourdough",
        "roastery", "beans", "matcha latte", "tea house", "tea bar",
        "croissant cafe", "bistro cafe", "concept cafe",
    ],

    "Dessert": [
        "dessert", "gelato", "ice cream", "froyo", "frozen yogurt", "popsicle",
        "shaved ice", "bingsu", "parfait", "waffle", "pancake", "crepe",
        "milkshake", "tiramisu", "brownie", "acai", "sorbet", 
        "snow ice", "mango sago", "yuzu sorbet",
    ],

    "Bubble Tea": [
        "bubble tea", "boba", "milk tea", "fruit tea", "pearl", 
        "tiger sugar", "brown sugar milk", "tea shop", "tea studio",
        "cheese tea", "macchiato tea", "each a cup"
    ],

    "Fast Food": [
        "fried chicken", "burger", "double cheeseburger", "fries",
        "chicken wrap", "fish burger", "pizza", "sub", "nuggets",
        "hot dog", "cheeseburger", "family meal",
        # Generic fast food names
        "express", "quick bites", "takeaway only"
    ],

    "Bakery": [
        "bakery", "bread", "pastry", "patisserie", "boulangerie",
        "cake shop", "cake", "muffin", "tart", "croissant", 
        "sourdough bakery", "loaf", "toast shop", "bagel",
        "artisan bread", "danish"
    ],

    "Food Court": [
        "food court", "food junction", "food republic", 
        "kopitiam", "the kitchen", "the food market",
    ],

    "Supermarket Food": [
        "supermarket", "ready to eat", "ready meal",
        "bento", "heat-and-eat", "pre-packed meal",
        "don don donki", "donki", "fairprice", "ntuc",
        "shokupan", "salad bowl", "microwave meal",
    ],


    "Restaurant": [
        # General restaurant terms
        "restaurant", "kitchen", "grill", "smokehouse", "steakhouse",
        "izakaya", "trattoria", "osteria", "cantina", "bistro",
        "hotpot", "bbq", "korean bbq", "yakitori", "ramen", "sushi",
        # Generic markers
        "dining", "house", "family restaurant", "chophouse",
        # International cuisine indicators (treated as restaurant)
        "thai", "indian", "korean", "japanese", "vietnamese",
        "turkish", "middle eastern", "greek", "mexican", "peranakan"
    ]
}


def classify_category(name):
    if not name:
        return None

    text = normalize(name)
    best_category = None
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1

        # Keep highest score
        if score > best_score:
            best_score = score
            best_category = category
        
        if best_category is None:
            best_category = "Restaurant"

    return best_category


rows = db.execute("SELECT id, name FROM restaurants").fetchall()

for row in rows:
    rest_id = row["id"]
    name = row["name"]

    category = classify_category(name)

    if category is None:
        continue

    db.execute(
        "UPDATE restaurants SET category = ? WHERE id = ?",
        (category, rest_id)
    )

conn.commit()
conn.close()
print("Completed assigning categories")