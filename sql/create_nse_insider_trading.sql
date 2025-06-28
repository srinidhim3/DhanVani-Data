CREATE TABLE IF NOT EXISTS nse_insider_trading (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    security_type TEXT,
    published_at TEXT NOT NULL
);