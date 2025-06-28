CREATE TABLE IF NOT EXISTS nse_brsr (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    pdf_link TEXT,
    xml_link_name TEXT,
    submission_date TEXT NOT NULL
);