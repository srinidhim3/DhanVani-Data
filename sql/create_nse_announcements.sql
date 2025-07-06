CREATE TABLE IF NOT EXISTS nse_announcements (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    description TEXT,
    published_at TEXT NOT NULL,
    company_symbol text,
    summary text
);