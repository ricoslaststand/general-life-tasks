from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    ynab_access_key: str
    mistral_access_key: str
    youtube_api_key: str
    postgres__db: str
    postgres__username: str
    postgres__url: str
    postgres__password: str
    postgres__port: int = Field(5432)

settings = Settings()
