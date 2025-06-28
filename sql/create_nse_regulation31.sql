CREATE TABLE IF NOT EXISTS nse_regulation31 (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    promoter_or_pacs_name TEXT,
    published_at TEXT NOT NULL
);