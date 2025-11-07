PRAGMA foreign_keys = ON;

-- Create neighborhoods table
CREATE TABLE IF NOT EXISTS neighborhoods (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

-- Create restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    neighborhood_id INTEGER,
    price_range TEXT,
    avg_rating REAL,
    FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(id)
);

-- Create cuisines table
CREATE TABLE IF NOT EXISTS cuisines (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

-- Create restaurant_cuisines table (many-to-many)
CREATE TABLE IF NOT EXISTS restaurant_cuisines (
    restaurant_id INTEGER,
    cuisine_id INTEGER,
    PRIMARY KEY (restaurant_id, cuisine_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (cuisine_id) REFERENCES cuisines(id)
);

-- Create vibes table
CREATE TABLE IF NOT EXISTS vibes (
    id INTEGER PRIMARY KEY,
    vibe TEXT UNIQUE
);

-- Create restaurant_vibes table (many-to-many)
CREATE TABLE IF NOT EXISTS restaurant_vibes (
    restaurant_id INTEGER,
    vibe_id INTEGER,
    PRIMARY KEY (restaurant_id, vibe_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (vibe_id) REFERENCES vibes(id)
);

-- Create menu_items table
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    item_name TEXT NOT NULL,
    price REAL,
    description TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- Create recommended_items table
CREATE TABLE IF NOT EXISTS recommended_items (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    menu_item_id INTEGER,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Create reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    restaurant_id INTEGER,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- Create preferences table
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    budget TEXT NOT NULL,
    occasion TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    dietary_restrictions TEXT NOT NULL,
    vibe TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);