from functools import reduce

from youtube_transcript_api import YouTubeTranscriptApi

from pyyoutube import Api

from repositories.video_repo import VideoRepo

# Add in API key
api = Api(api_key="")

pickleball_channels: list[str] = [
      "@thatpickleballguy",
      "@Richard_pickleball",
      "@Ryanfupickleball",
      "@pickleballplaybook",
      "@johncincolapickleball"
]

video_repo = VideoRepo()

def main():
	# channel = api.get_channel_info(for_handle="@thatpickleballguy")
	# print(channel.items[0].to_dict())

	# video_id = "C3Cagcs3r9s"
	ytt_api = YouTubeTranscriptApi()
	fetched_transcript = ytt_api.fetch(video_id=video_id)
	
	text = reduce(lambda x, y: x + y.text, fetched_transcript, "")

	print(text)

def load_videos_for_channels():
      for handle in pickleball_channels:

if __name__ == "__main__":
    main()
