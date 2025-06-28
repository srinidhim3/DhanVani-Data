CREATE TABLE IF NOT EXISTS nse_secretarial_compliance (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    pdf_link TEXT,
    xml_link TEXT,
    financial_year TEXT,
    submission_type TEXT,
    published_at TEXT NOT NULL
);