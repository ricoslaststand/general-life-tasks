CREATE TABLE videos (
    id BIGSERIAL PRIMARY KEY,
    youtube_channel_id VARCHAR(64) UNIQUE NOT NULL,  -- e.g. UCxxxxxx
    name TEXT NOT NULL,
    description TEXT,
    summarization TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE channels (
    id BIGSERIAL PRIMARY KEY,
    youtube_video_id VARCHAR(64) UNIQUE NOT NULL,  -- e.g. dQw4w9WgXcQ
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMPTZ,
    duration INTERVAL,  -- if you want to store parsed duration
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()  
);
