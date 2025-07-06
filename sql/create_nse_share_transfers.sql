CREATE TABLE IF NOT EXISTS nse_share_transfers (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    period_end_date TEXT NOT NULL,
    published_at TEXT NOT NULL,
    company_symbol text,
    summary text
);