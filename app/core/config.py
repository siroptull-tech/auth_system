from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    DATABASE_URL: str = "postgresql://auth_user:changeme@localhost:5432/auth_db"
    JWT_SECRET: str = "change-me-before-deploy"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    APP_NAME: str = "Auth System"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    DB_USER: str = "auth_user"
    DB_PASSWORD: str = "changeme"
    DB_NAME: str = "auth_db"
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: list[str] = ["http://localhost:8000"]


settings = Settings()
