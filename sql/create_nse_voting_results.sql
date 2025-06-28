CREATE TABLE IF NOT EXISTS nse_voting_results (
    id SERIAL PRIMARY KEY,
    guid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    link TEXT,
    meeting_date TEXT NOT NULL,
    published_at TEXT NOT NULL
);