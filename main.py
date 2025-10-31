from limits import RateLimitItemPerSecond
from loguru import logger
from pyyoutube import Api

from config import db, get_db_healthcheck, settings
from models import PickleballShot
from repositories import ChannelRepo, VideoRepo
from services.youtube_service import YoutubeService
from utils import job_management

api = Api(api_key=settings.youtube_api_key)

pickleball_channels: list[str] = [
      "@thatpickleballguy",
      "@Richard_pickleball",
      "@Ryanfupickleball",
      "@pickleballplaybook",
      "@johncincolapickleball",
      "@Jackmunropickleball",
      "@roscoebellamy",
      "@CallieSmith",
      "@theflyingpickleacademy",
      "@TroyAkin"
]

pickleball_shots = [
    # Groundstrokes
    PickleballShot("Forehand Drive", ["Forehand", "Drive", "Groundstroke", "Offense"]),
    PickleballShot("Backhand Drive", ["Backhand", "Drive", "Groundstroke", "Offense"]),
    PickleballShot("Forehand Topspin", ["Forehand", "Topspin", "Groundstroke"]),
    PickleballShot("Backhand Topspin", ["Backhand", "Topspin", "Groundstroke"]),
    PickleballShot("Forehand Slice", ["Forehand", "Slice", "Groundstroke", "Defense"]),
    PickleballShot("Backhand Slice", ["Backhand", "Slice", "Groundstroke", "Defense"]),

    # Drops
    PickleballShot("Forehand Drop", ["Forehand", "Drop", "Soft", "Transition"]),
    PickleballShot("Backhand Drop", ["Backhand", "Drop", "Soft", "Transition"]),
    PickleballShot("Third Shot Drop", ["Drop", "Third Shot", "Soft", "Setup"]),
    PickleballShot("Transition Drop", ["Drop", "Transition", "Soft"]),

    # Dinks
    PickleballShot("Forehand Dink", ["Forehand", "Dink", "Soft", "Net Play"]),
    PickleballShot("Backhand Dink", ["Backhand", "Dink", "Soft", "Net Play"]),
    PickleballShot("Crosscourt Dink", ["Dink", "Crosscourt", "Soft", "Net Play"]),
    PickleballShot("Straight Dink", ["Dink", "Down-the-Line", "Soft", "Net Play"]),
    PickleballShot("Topspin Dink", ["Dink", "Topspin", "Aggressive", "Net Play"]),
    PickleballShot("Dink Volley", ["Dink", "Volley", "Soft", "Net Play"]),

    # Volleys
    PickleballShot("Forehand Volley", ["Forehand", "Volley", "Net Play", "Offense"]),
    PickleballShot("Backhand Volley", ["Backhand", "Volley", "Net Play", "Offense"]),
    PickleballShot("Punch Volley", ["Volley", "Punch", "Offense", "Quick Reaction"]),
    PickleballShot("Block Volley", ["Volley", "Block", "Defense", "Reset"]),
    PickleballShot("Drop Volley", ["Volley", "Drop", "Soft", "Net Play"]),

    # Serves
    PickleballShot("Forehand Serve", ["Serve", "Forehand", "Baseline"]),
    PickleballShot("Backhand Serve", ["Serve", "Backhand", "Baseline"]),
    PickleballShot("Topspin Serve", ["Serve", "Topspin", "Offense"]),
    PickleballShot("Slice Serve", ["Serve", "Slice", "Spin"]),
    PickleballShot("Power Serve", ["Serve", "Drive", "Offense"]),
    PickleballShot("Lob Serve", ["Serve", "Lob", "Defensive"]),

    # Returns
    PickleballShot("Forehand Return", ["Return", "Forehand", "Baseline"]),
    PickleballShot("Backhand Return", ["Return", "Backhand", "Baseline"]),
    PickleballShot("Chip Return", ["Return", "Slice", "Control"]),
    PickleballShot("Deep Return", ["Return", "Deep", "Defensive"]),

    # Lobs
    PickleballShot("Offensive Lob", ["Lob", "Offense", "Overhead Setup"]),
    PickleballShot("Defensive Lob", ["Lob", "Defense", "Reset"]),
    PickleballShot("Forehand Lob", ["Forehand", "Lob", "Defense"]),
    PickleballShot("Backhand Lob", ["Backhand", "Lob", "Defense"]),

    # Smashes & Putaways
    PickleballShot("Overhead Smash", ["Smash", "Overhead", "Putaway", "Offense"]),
    PickleballShot("Forehand Putaway", ["Forehand", "Putaway", "Offense"]),
    PickleballShot("Backhand Putaway", ["Backhand", "Putaway", "Offense"]),
    PickleballShot("Erne", ["Volley", "Offense", "Special", "Net Play"]),
    PickleballShot("ATP (Around The Post)", ["Special", "Offense", "Trick Shot"]),

    # Resets & Specialty Shots
    PickleballShot("Reset Shot", ["Reset", "Defense", "Soft"]),
    PickleballShot("Counterattack", ["Counter", "Reaction", "Offense"]),
    PickleballShot("Speedup", ["Volley", "Speedup", "Offense", "Quick Reaction"]),
    PickleballShot("Roll Volley", ["Volley", "Topspin", "Aggressive"]),
]

get_db_healthcheck()

channel_repo = ChannelRepo(db=db)
video_repo = VideoRepo(db=db)
youtube_service = YoutubeService(yt_client=api, channel_repo=channel_repo, video_repo=video_repo)

def main():
      for handle in pickleball_channels:
            try:
                  pb_channel = __retrieve_youtube_channel(youtube_service=youtube_service, handle=handle)
                  channel_repo.insert_channel(channel=pb_channel)
                  logger.info(f"Inserted channel with ID {pb_channel.id} into database...")
                  
                  if pb_channel:
                        videos = __retrieve_videos_by_channel_id(pb_channel.id)
                        logger.info(f"Grabbed videos for channel {pb_channel.id}")
                        for v in videos:
                              logger.info(f"Video to be Inserted: ID: {v.id}, Title: {v.title}")
                              video_repo.insert_video(v)
                              __add_transcript_to_database(video_id=v.id)
                        logger.info(f"Finished adding the videos for {pb_channel.title}")
            except Exception as e:
                  print(e)

@job_management.job_limiter(rate_limit=RateLimitItemPerSecond(1, 1), waiting_time=5)
def __retrieve_youtube_channel(youtube_service, handle: str):
      print("retrieving channel")
      pb_channel = youtube_service.get_channel_info_by_handle(handle=handle)
      print("Successfully retrieved the PB channel")
      return pb_channel

@job_management.job_limiter(rate_limit=RateLimitItemPerSecond(1, 1), waiting_time=5)
def __retrieve_videos_by_channel_id(channel_id: str):
      return youtube_service.get_all_videos_by_channel_id(channel_id=channel_id)

@job_management.job_limiter(rate_limit=RateLimitItemPerSecond(1, 1))
def __add_transcript_to_database(video_id: str) -> None:
      try:
            transcript = youtube_service.transcribe_video_by_id(video_id=video_id)
            if transcript and len(transcript) > 0:
                  video_repo.add_youtube_transcript(video_id=video_id, transcript=transcript)
      except Exception as e:
            print(e)

if __name__ == "__main__":
    logger.info("Running pickleball video extractor...")
    main()
