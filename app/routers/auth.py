from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import GoogleLoginRequest, RefreshRequest, TokenPair, LogoutRequest
from app.schemas.user import UserClaims
from app.core.revocation import revoke_refresh, is_refresh_revoked

router = APIRouter(prefix="/auth", tags=["auth"])

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

@router.post("/refresh", response_model=TokenPair)
def refresh_tokens(body: RefreshRequest):
    # 1) 블랙리스트 여부 우선 확인
    if is_refresh_revoked(body.refresh_token):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        payload = decode_token(body.refresh_token)
        if payload.get("typ") != "refresh":
            raise ValueError("Not a refresh token")
        user_claims = payload.get("usr") or {}
        exp_unix = payload.get("exp")  # 로그아웃 시 보관용
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = create_access_token(user_claims)
    new_refresh = create_refresh_token(user_claims)

    return TokenPair(access_token=access, refresh_token=new_refresh)

@router.post("/logout")
def logout(body: LogoutRequest):
    """
    클라이언트: 로컬/쿠키에 저장된 access/refresh 삭제
    서버(선택): 전달된 refresh_token이 있으면 블랙리스트 등록
    """
    if body.refresh_token:
        # exp를 알 수 있으면 함께 저장 (없어도 보수적 TTL로 저장됨)
        try:
            payload = decode_token(body.refresh_token)
            exp_unix = payload.get("exp")
        except Exception:
            exp_unix = None
        revoke_refresh(body.refresh_token, exp_unix)

    # 서버는 상태를 거의 가지지 않으므로 200 OK만 반환
    return {"detail": "logged out"}
