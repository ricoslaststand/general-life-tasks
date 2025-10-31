from datetime import datetime
from functools import reduce
from typing import List, Optional

import scrapetube
from pyyoutube import Api
from youtube_transcript_api import YouTubeTranscriptApi

from models import YoutubeChannel, YoutubeVideo
from repositories import ChannelRepo, VideoRepo

class YoutubeService:
    def __init__(self, yt_client: Api, channel_repo: ChannelRepo, video_repo: VideoRepo):
        self.yt_client = yt_client
        self.channel_repo = channel_repo
        self.video_repo = video_repo
        self.transcription_api = YouTubeTranscriptApi()

    def insert_channels(self, channels: List[YoutubeChannel]) -> None:
        for channel in channels:
            self.channel_repo.insert_channel(channel=channel)

    def get_all_videos_by_channel_id(self, channel_id: str) -> List[YoutubeVideo]:
        videos = scrapetube.get_channel(channel_id=channel_id)
        video_ids = []

        for video in videos:
            video_ids.append(video["videoId"])

        videos_list: List[YoutubeVideo] = []

        for id in video_ids:
            response = self.yt_client.get_video_by_id(video_id=id)
            if len(response.items) > 0:
                 video_metadata = response.items[0]
                 videos_list.append(
                    YoutubeVideo(
                        id=video_metadata.id,
                        title=video_metadata.snippet.title,
                        description=video_metadata.snippet.description,
                        channel_id=video_metadata.snippet.channelId,
                        published_at=datetime.strptime(video_metadata.snippet.publishedAt, "%Y-%m-%dT%H:%M:%SZ")
                    )
                 )
        
        return videos_list

    def get_video_by_id(self, id: str) -> Optional[YoutubeVideo]:
        return None

    def get_channel_info_by_handle(self, handle: str) -> Optional[YoutubeChannel]:
        response = self.yt_client.get_channel_info(for_handle=handle)
        if len(response.items) == 0:
            return None
        
        channel_info = response.items[0].to_dict()

        return YoutubeChannel(
            handle=channel_info["snippet"]["customUrl"],
            id=channel_info["id"],
            title=channel_info["snippet"]["title"],
            description=channel_info["snippet"]["description"]
        )

    def transcribe_video_by_id(self, video_id: str) -> str:
        response = self.transcription_api.fetch(video_id)
        text = reduce(lambda x, y: x + y.text, response, " ")

        return text
    

