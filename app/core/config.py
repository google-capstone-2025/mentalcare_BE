# app/core/config.py
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices, field_validator


class Settings(BaseSettings):
    # pydantic-settings v2 구성
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,   # 환경변수 대소문자 구분
    )

    # ---- 앱 메타 ----
    APP_NAME: str = Field("MentalCare BE", description="Application name")
    APP_ENV: Literal["development", "staging", "production"] = Field(
        "development", description="App environment"
    )

    # ---- DB ----
    DATABASE_URL: str = Field(..., description="SQLAlchemy URL")

    # ---- JWT/보안 ----
    # .env에는 JWT_ALGORITHM 이라고 되어 있어 호환용 alias 제공
    JWT_ALG: str = Field(
        "HS256",
        description="JWT signing algorithm",
        validation_alias=AliasChoices("JWT_ALG", "JWT_ALGORITHM"),
    )
    JWT_SECRET: str = Field(..., description="JWT signing secret")

    ACCESS_TOKEN_MIN: int = Field(30, description="Access token lifetime (minutes)")
    REFRESH_TOKEN_DAYS: int = Field(7, description="Refresh token lifetime (days)")

    # ---- OAuth ----
    GOOGLE_CLIENT_ID: str = Field(..., description="Google OAuth Web Client ID")

    # ---- 파생 유틸 ----
    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"

    @field_validator("DATABASE_URL")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        # 흔한 실수 방지: postgresql 스킴 권장, 공백 제거, 빈값 방지
        v = v.strip()
        if not v:
            raise ValueError("DATABASE_URL is empty")
        # sqlalchemy는 postgresql+psycopg2 권장
        if v.startswith("postgres://"):
            # SQLAlchemy 2.x 호환을 위해 자동 보정
            v = "postgresql+psycopg2://" + v[len("postgres://") :]
        if not (v.startswith("postgresql://") or v.startswith("postgresql+")):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql+psycopg2://' (or 'postgresql://')"
            )
        return v


settings = Settings()
