# app/core/security.py
from datetime import datetime, timedelta
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

ALGO = settings.JWT_ALG
SECRET = settings.JWT_SECRET

# ─── 토큰 발급/검증 (이미 있으면 유지) ─────────────────────────
def create_access_token(sub: str, expires_minutes: int = settings.ACCESS_TOKEN_MIN) -> str:
    payload = {
        "sub": sub,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def create_refresh_token(sub: str, expires_days: int = settings.REFRESH_TOKEN_DAYS) -> str:
    payload = {
        "sub": sub,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=expires_days),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGO])

# ─── 요청에서 현재 유저 꺼내기 ───────────────────────────────
bearer = HTTPBearer(auto_error=False)

@dataclass
class CurrentUser:
    id: str | None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> CurrentUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return CurrentUser(id=str(user_id))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
