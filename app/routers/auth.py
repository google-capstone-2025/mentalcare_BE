from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import GoogleLoginRequest, RefreshRequest, TokenPair, LogoutRequest
from app.schemas.user import UserClaims

router = APIRouter(prefix="/auth", tags=["auth"])

# 🔹 Google 로그인
@router.post("/google", response_model=TokenPair)
def login_with_google(body: GoogleLoginRequest):
    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential,
            grequests.Request(),
            audience=settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    claims = UserClaims(
        sub=idinfo.get("sub"),
        email=idinfo.get("email"),
        name=idinfo.get("name"),
        picture=idinfo.get("picture"),
    ).model_dump()

    access = create_access_token(claims)
    refresh = create_refresh_token(claims)
    return TokenPair(access_token=access, refresh_token=refresh)


# 🔹 Refresh 토큰 재발급
@router.post("/refresh", response_model=TokenPair)
def refresh_tokens(body: RefreshRequest):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("typ") != "refresh":
            raise ValueError("Not a refresh token")
        user_claims = payload.get("usr") or {}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = create_access_token(user_claims)
    new_refresh = create_refresh_token(user_claims)

    return TokenPair(access_token=access, refresh_token=new_refresh)


# 🔹 로그아웃 (서버는 상태를 저장하지 않음)
@router.post("/logout")
def logout(body: LogoutRequest):
    """
    클라이언트: 로컬/쿠키에 저장된 access/refresh 삭제
    서버: 블랙리스트 관리하지 않음 (무상태 설계)
    """
    return {"detail": "logged out"}
