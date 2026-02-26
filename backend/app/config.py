"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MongoDB
    mongo_url: str = "mongodb://admin:password@localhost:27017/pioyan_chat?authSource=admin"
    mongo_db: str = "pioyan_chat"

    # JWT
    jwt_secret: str = "change-me-to-a-random-secret-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    # FastAPI
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    # File upload
    upload_dir: str = "uploads"
    max_file_size_mb: int = 10


settings = Settings()
