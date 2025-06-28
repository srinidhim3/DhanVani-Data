CREATE TABLE IF NOT EXISTS nse_related_party_transactions (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    period_end_date TEXT NOT NULL,
    published_at TEXT NOT NULL
);