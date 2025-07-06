CREATE TABLE IF NOT EXISTS nse_shareholding_pattern (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    as_on_date TEXT NOT NULL,
    promoter_holding REAL,
    public_holding REAL,
    employee_trust_holding REAL,
    revised_status TEXT,
    submission_date TEXT NOT NULL,
    revision_date TEXT,
    published_at TEXT NOT NULL,
    company_symbol text,
    summary text
);