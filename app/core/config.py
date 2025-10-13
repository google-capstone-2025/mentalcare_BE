from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str = Field(..., description="OAuth Web client ID")
    JWT_SECRET: str = Field(..., description="JWT signing secret")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_MIN: int = 30       # 액세스 토큰 만료(분)
    REFRESH_TOKEN_DAYS: int = 7      # 리프레시 토큰 만료(일)

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
