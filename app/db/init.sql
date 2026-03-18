CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    source TEXT,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMP,
    content TEXT,
    fetched_at TIMESTAMP DEFAULT NOW()
);