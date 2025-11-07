import sqlite3, os

# Where your DB lives
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.db")

# Create /data folder if missing
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

# If DB already exists, do nothing
if os.path.exists(DB_PATH):
    print("✔ Database already exists. No changes made.")
    exit()

# Create DB
conn = sqlite3.connect(DB_PATH)
db = conn.cursor()

print("⚙️ Creating database...")

# SCHEMA
db.executescript("""
CREATE TABLE neighborhoods (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    neighborhood_id INTEGER,
    price_range TEXT,
    avg_rating REAL,
    FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(id)
);

CREATE TABLE cuisines (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE restaurant_cuisines (
    restaurant_id INTEGER,
    cuisine_id INTEGER,
    PRIMARY KEY (restaurant_id, cuisine_id)
);

CREATE TABLE vibes (
    id INTEGER PRIMARY KEY,
    vibe TEXT UNIQUE
);

CREATE TABLE restaurant_vibes (
    restaurant_id INTEGER,
    vibe_id INTEGER,
    PRIMARY KEY (restaurant_id, vibe_id)
);

CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    item_name TEXT NOT NULL,
    price REAL,
    description TEXT
);

CREATE TABLE recommended_items (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    menu_item_id INTEGER
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    restaurant_id INTEGER,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
