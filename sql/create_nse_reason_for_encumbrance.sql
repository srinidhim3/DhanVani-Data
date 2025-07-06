CREATE TABLE IF NOT EXISTS nse_reason_for_encumbrance (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    promoter_name TEXT,
    published_at TEXT,
    company_symbol text,
    summary text
);