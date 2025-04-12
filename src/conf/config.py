from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:567234@localhost:5432/postgres"

    JWT_SECRET: str  = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    REDIS_URL: str = "redis://localhost"

    MAIL_USERNAME: EmailStr = "yulgoit@meta.ua"
    MAIL_PASSWORD: str = "Qwertyasdfgh121"
    MAIL_FROM: EmailStr = "yulgoit@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = False

    CLOUDINARY_NAME: str = "dbpztbpex"
    CLOUDINARY_API_KEY: int = 239867989221579
    CLOUDINARY_API_SECRET: str = "Meg5ZOYOZhlOphLj0VO3XipXnJk"

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

settings = Settings()