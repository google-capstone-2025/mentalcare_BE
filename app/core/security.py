from datetime import datetime, timedelta, timezone
import jwt
from typing import Any, Dict
from app.core.config import settings

def _exp(dt: timedelta) -> int:
    return int((datetime.now(timezone.utc) + dt).timestamp())

def create_access_token(user_claims: Dict[str, Any]) -> str:
    # user_claims 예: {"sub": "...", "email": "...", "name": "...", "picture": "..."}
    payload = {
        "typ": "access",
        "usr": user_claims,
        "exp": _exp(timedelta(minutes=settings.ACCESS_TOKEN_MIN))
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def create_refresh_token(user_claims: Dict[str, Any]) -> str:
    payload = {
        "typ": "refresh",
        "usr": user_claims,
        "exp": _exp(timedelta(days=settings.REFRESH_TOKEN_DAYS))
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
