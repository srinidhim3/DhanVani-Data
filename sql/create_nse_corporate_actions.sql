CREATE TABLE IF NOT EXISTS nse_corporate_actions (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    description TEXT,
    published_at TEXT NOT NULL,
    ex_date TEXT,
    series TEXT,
    purpose TEXT,
    face_value REAL,
    record_date TEXT NOT NULL,
    company_symbol text,
    summary text
);