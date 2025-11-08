PRAGMA foreign_keys = ON;

-- ===========================================================
-- 1. NEIGHBORHOODS / REGIONS
-- ===========================================================
CREATE TABLE IF NOT EXISTS neighborhoods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

-- ===========================================================
-- 2. RESTAURANTS (core entity: restaurants + hawker centres)
-- ===========================================================
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Basic info
    name TEXT NOT NULL,
    license_name TEXT,
    address TEXT,
    unit_no TEXT,
    level TEXT,
    postal TEXT,
    neighborhood_id INTEGER,

    -- Classification / metadata
    type TEXT DEFAULT 'Restaurant',          -- e.g., 'Restaurant', 'Hawker Centre', 'Cafe'
    is_hawker INTEGER DEFAULT 0,             -- 0 = Restaurant, 1 = Hawker
    cuisine TEXT,                            -- from GeoJSON or APIs
    price_range TEXT,                        -- $, $$, $$$ etc.
    average_cost REAL,                       -- numerical version (optional)
    rating REAL,                             -- average rating from APIs or reviews
    total_reviews INTEGER DEFAULT 0,         -- review count from APIs
    phone_number TEXT,
    website TEXT,
    opening_hours TEXT,                      -- JSON string (for multi-day schedules)
    amenities TEXT,                          -- JSON or comma-separated (wifi, halal, etc.)

    -- GeoJSON / geolocation support
    latitude REAL,
    longitude REAL,
    raw_properties TEXT,                     -- store full GeoJSON properties for reference

    -- Foreign key relationships
    FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(id)
);

-- ===========================================================
-- 3. CUISINES
-- ===========================================================
CREATE TABLE IF NOT EXISTS cuisines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS restaurant_cuisines (
    restaurant_id INTEGER,
    cuisine_id INTEGER,
    PRIMARY KEY (restaurant_id, cuisine_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (cuisine_id) REFERENCES cuisines(id)
);

-- ===========================================================
-- 4. VIBES (used for tagging ambiance / style)
-- ===========================================================
CREATE TABLE IF NOT EXISTS vibes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vibe TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS restaurant_vibes (
    restaurant_id INTEGER,
    vibe_id INTEGER,
    PRIMARY KEY (restaurant_id, vibe_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (vibe_id) REFERENCES vibes(id)
);

-- ===========================================================
-- 5. MENU ITEMS
-- ===========================================================
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    item_name TEXT NOT NULL,
    price REAL,
    description TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE IF NOT EXISTS recommended_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    menu_item_id INTEGER,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- ===========================================================
-- 6. USERS
-- ===========================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    security_question TEXT NOT NULL,
    security_answer TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================================
-- 7. REVIEWS (user-submitted)
-- ===========================================================
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    restaurant_id INTEGER,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- ===========================================================
-- 8. PREFERENCES (used for personalized recommendations)
-- ===========================================================
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    region TEXT,
    budget TEXT,
    occasion TEXT,
    cuisine TEXT,
    dietary_restrictions TEXT,
    vibe TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);