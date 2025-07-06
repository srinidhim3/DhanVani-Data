CREATE TABLE IF NOT EXISTS nse_board_meetings (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    meeting_date TEXT NOT NULL,
    published_at TEXT NOT NULL,
    company_symbol text,
    summary text
);