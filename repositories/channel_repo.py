from sqlalchemy import Engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert


from models import YoutubeChannel

class ChannelRepo:
    def __init__(self, db: Engine):
        self.db = db
        self.channel_table = Table(
            "youtube_channel",
            MetaData(),
            autoload_with=self.db
        )
    
    def get_all_channels(self) -> list:
        return []
    
    def get_channel_by_id(self, youtube_channel_id: str) -> YoutubeChannel | None:
        return None
    
    def insert_channel(self, channel: YoutubeChannel) -> None:
        with self.db.begin() as connection:
            stmt = insert(self.channel_table).values(id=channel.id, title=channel.title, description=channel.description)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])

            connection.execute(stmt)
    