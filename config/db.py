from loguru import logger
from sqlalchemy import create_engine, text, URL

from .settings import settings

db = create_engine(
    URL.create(
        "postgresql+psycopg2",
        username=settings.postgres__username,
        password=settings.postgres__password,
        host=settings.postgres__url,
        port=settings.postgres__port,
        database=settings.postgres__db
    )
)

def healthcheck() -> bool:
    with db.begin() as connection:
        connection.execute(text("SELECT 1"))
        logger.info("Successfully connected to the database")
