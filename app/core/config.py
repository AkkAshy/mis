from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-calm-dew-a86c7qwq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()