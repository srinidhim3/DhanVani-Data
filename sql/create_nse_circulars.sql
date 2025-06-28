CREATE TABLE IF NOT EXISTS nse_circulars (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    published_at TEXT NOT NULL
);