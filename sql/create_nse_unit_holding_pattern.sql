CREATE TABLE IF NOT EXISTS nse_unit_holding_pattern (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    as_on_date TEXT NOT NULL,
    published_at TEXT NOT NULL
);