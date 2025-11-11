# app/routers/auth.py
from app.models.enum import Provider
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import GoogleLoginRequest, RefreshRequest, TokenPair, LogoutRequest
# from app.schemas.user import UserClaims  # picture 제거에 맞춰 직접 dict 구성으로 변경

from app.db.session import get_db
from app.models.user import Users, OAuthIdentities

router = APIRouter(prefix="/auth", tags=["auth"])

# 🔹 Google 로그인 (+ DB upsert)
@router.post("/google", response_model=TokenPair)
def login_with_google(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential,
            grequests.Request(),
            audience=settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    google_sub = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name")
    locale = idinfo.get("locale")

    if not google_sub or not email:
        raise HTTPException(status_code=400, detail="Google profile missing required fields")

    # 1) Users upsert (email 기준)
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        user = Users(email=email, name=name, locale=locale)
        db.add(user)
        db.flush()  # user.id 확보
    else:
        # 선택: 최신 정보로 동기화 (name/locale)
        user.name = name or user.name
        user.locale = locale or user.locale

    # 2) OAuthIdentities upsert (provider + subject)
    oauth = (
        db.query(OAuthIdentities)
        .filter(
            OAuthIdentities.user_id == user.id,
            OAuthIdentities.provider == Provider.GOOGLE,   # ProviderSAEnum 사용 시 ProviderSAEnum.google
        )
        .first()
    )
    if not oauth:
        oauth = OAuthIdentities(
            user_id=user.id,
            provider=Provider.GOOGLE,                      # ProviderSAEnum 사용 시 ProviderSAEnum.google
            subject=google_sub,
            raw_claims=idinfo,
        )
        db.add(oauth)
    else:
        oauth.subject = google_sub
        oauth.raw_claims = idinfo

    db.commit()
    db.refresh(user)

    # 3) JWT에 넣을 클레임 (picture 제거)
    claims = {
        "sub": str(user.id),   # 내부 UUID를 주 식별자로
        "email": user.email,
        "name": user.name,
        "locale": user.locale,
    }

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
def logout(_: LogoutRequest):
    """
    클라이언트: 로컬/쿠키에 저장된 access/refresh 삭제
    서버: 블랙리스트 관리하지 않음 (무상태 설계)
    """
    return {"detail": "logged out"}
