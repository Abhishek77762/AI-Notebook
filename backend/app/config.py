from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    FILE_DIR: str = Field(default="./data/files", env="FILE_DIR")
    ASSET_DIR: str = Field(default="./data/assets", env="ASSET_DIR")
    JWT_EXPIRE_MINUTES: int = 60

    PIPER_BIN: Optional[str] = None
    PIPER_VOICE: Optional[str] = None
    JWT_SECRET: str = "supersecretkey"
    class Config:
        env_file = ".env"

settings = Settings()
