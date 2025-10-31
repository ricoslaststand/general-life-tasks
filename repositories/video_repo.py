from loguru import logger
from sqlalchemy import update, Engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert

from models.Youtube import YoutubeVideo

class VideoRepo:
    def __init__(self, db: Engine):
        self.db = db
        self.video_table = Table(
            "youtube_video",
            MetaData(),
            autoload_with=self.db
        )

    def insert_video(
            self,
            video: YoutubeVideo) -> None:
        with self.db.begin() as connection:
            stmt = insert(self.video_table).values(
                id=video.id,
                title=video.title,
                description=video.description,
                channel_id=video.channel_id,
                published_at=video.published_at,
            )
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])

            connection.execute(stmt)
            logger.info("Added video to database")
        
    
    def get_video_status(self):
        return
    
    def get_video(self, video_id: str):
        return

    def add_youtube_transcript(self, video_id: str, transcript: str) -> None:
        with self.db.begin() as connection:
            stmt = update(self.video_table).where(self.video_table.c.id == video_id).values(
                transcript=transcript
            )
            connection.execute(stmt)
