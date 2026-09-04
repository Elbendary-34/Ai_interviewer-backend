# Configurations & Env Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "IntervYou AI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Infrastructure Services
    REDIS_URL: str = "redis://localhost:6379"
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/intervyou_db"
    
    # LiveKit WebRTC Configuration
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secretsecretsecretsecretsecretsecretsecret"
    LIVEKIT_URL: str = "ws://localhost:7880"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()