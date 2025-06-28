CREATE TABLE IF NOT EXISTS nse_investor_complaints (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    quarter_ending_date TEXT NOT NULL,
    published_at TEXT NOT NULL
);