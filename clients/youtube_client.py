from dataclasses import dataclass

from pydantic import SecretStr
from pyyoutube import Api

@dataclass
class ChannelDto:
    id: str
    title: str
    description: str
    handle: str

@dataclass
class VideoDto:
    id: str
    description: str

class YoutubeClient:
    def __init__(self, api_key: SecretStr):
        self.youtube_api_client = Api(api_key=api_key)
        
    def get_channel_by_handle(self, handle: str):
        channel = self.youtube_api_client.get_channel_info(for_handle=handle)

    def get_videos_by_channel_id(self, channel_id: str) -> list[VideoDto]:
        return []

    def get_video_by_id(video_id: str) -> VideoDto | None:
        return

    def get_video_transcript_by_id(video_id: str) -> str | None:
        return 
