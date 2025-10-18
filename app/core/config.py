# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # v2에서는 class Config 대신 model_config 사용!
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    DATABASE_URL: str = "postgresql+psycopg2://mental_admin:MyPass123@localhost:5432/mentalcare"

    # 필수 환경변수 (없으면 앱 시작 시 ValidationError)
    GOOGLE_CLIENT_ID: str = Field(..., description="OAuth Web client ID")
    JWT_SECRET: str = Field(..., description="JWT signing secret")

    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_MIN: int = 30
    REFRESH_TOKEN_DAYS: int = 7

settings = Settings()
