from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class YoutubeChannel(BaseModel):
    id: str
    title: str
    description: str
    handle: str

class YoutubeVideo(BaseModel):
    id: str
    title: str
    description: str
    published_at: datetime
    channel_id: str
    transcript: Optional[str] = None
