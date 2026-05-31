CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    link TEXT,
    closed TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_categories (
    event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
    category_id TEXT REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, category_id)
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_sources (
    event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
    source_id TEXT REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, source_id)
);

CREATE TABLE IF NOT EXISTS event_geometry (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
    geometry_type TEXT NOT NULL,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    event_date TIMESTAMP NOT NULL,
    magnitude_value DOUBLE PRECISION,
    magnitude_unit TEXT
);