CREATE TABLE IF NOT EXISTS wildfire_events (
    id         TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    longitude  DOUBLE PRECISION,
    latitude   DOUBLE PRECISION,
    event_date TIMESTAMP
);
