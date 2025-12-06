import os
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = Field(default="sqlite:///./db.sqlite3", env="DATABASE_URL")

    # App web
    AUTH_SERVICE_URL: str = Field(default=f"http://127.0.0.1:8000", env="AUTH_SERVICE_URL")
    APP_SESSION_SECRET: SecretStr = Field(default=SecretStr("change-me-please-change-me-32-bytes"), env="APP_SESSION_SECRET")
    COOKIE_NAME: str = Field(default="session", env="COOKIE_NAME")
    COOKIE_SECURE: bool = Field(default=False, env="COOKIE_SECURE")
    COOKIE_SAMESITE: str = Field(default="lax", env="COOKIE_SAMESITE")

    # JWT/Auth
    SECRET_KEY: Optional[SecretStr] = Field(default=None, env="SECRET_KEY")
    PRIVATE_KEY_PATH: Optional[str] = Field(default=None, env="PRIVATE_KEY_PATH")
    PUBLIC_KEY_PATH: Optional[str] = Field(default=None, env="PUBLIC_KEY_PATH")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Email & Vérification
    SKIP_EMAIL_VERIFICATION: bool = Field(default=False, env="SKIP_EMAIL_VERIFICATION")
    EMAIL_BACKEND: str = Field(default="console", env="EMAIL_BACKEND")  # console, file, smtp
    EMAIL_VERIFICATION_TTL: int = Field(default=86400, env="EMAIL_VERIFICATION_TTL")  # 24h en secondes
    RESET_TOKEN_TTL: int = Field(default=3600, env="RESET_TOKEN_TTL")  # 1h en secondes
    BASE_URL: str = Field(default="http://localhost:8001", env="BASE_URL")  # URL de base pour liens email
    
    # SMTP (optionnel, pour production)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=None, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[SecretStr] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")

    # DVC/DagsHub (optionnel)
    DAGSHUB_USER: Optional[str] = Field(default=None, env="DAGSHUB_USER")
    DAGSHUB_REPO: Optional[str] = Field(default=None, env="DAGSHUB_REPO")
    DAGSHUB_TOKEN: Optional[str] = Field(default=None, env="DAGSHUB_TOKEN")

    # MLflow
    MLFLOW_PORT: int = Field(default=5001, env="MLFLOW_PORT")

    # Services
    FASTAPI_PORT: int = Field(default=8000, env="FASTAPI_PORT")
    AIRFLOW_WEB_PORT: int = Field(default=8080, env="AIRFLOW_WEB_PORT")

    # CORS & Redis
    CORS_ORIGINS: str = Field(default="http://localhost:8001,http://127.0.0.1:8001", env="CORS_ORIGINS")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Environnement
    APP_ENV: str = Field(default="development", env="APP_ENV")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()