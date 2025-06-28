CREATE TABLE IF NOT EXISTS nse_annual_reports (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    report_date TEXT NOT NULL
);