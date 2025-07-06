CREATE TABLE IF NOT EXISTS nse_regulation29 (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    acquirer_name TEXT,
    published_at TEXT NOT NULL,
    company_symbol text,
    summary text
);