from dataclasses import dataclass


@dataclass
class Video:
    id: int
    youtube_id: str

@dataclass
class Channel:
    id: int
    youtube_id: str
