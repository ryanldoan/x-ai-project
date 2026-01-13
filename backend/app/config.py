from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Get the project root directory (2 levels up from this file)
BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    grok_api_key: str
    grok_api_url: str = "https://api.x.ai/v1"
    database_url: str = "sqlite+pysqlite:///./posts.db"
    
    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

settings = Settings()

