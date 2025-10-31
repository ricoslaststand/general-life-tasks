CREATE TABLE IF NOT EXISTS youtube_channel (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()  
);

CREATE TABLE IF NOT EXISTS youtube_video (
    id VARCHAR(64) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    channel_id VARCHAR(64) NOT NULL REFERENCES youtube_channel(id) ON DELETE CASCADE,
    transcript TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_youtube_channel_id ON youtube_video(channel_id)
