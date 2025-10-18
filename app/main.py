# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, retrieve, aggregate, compose, uploads
from app.core.security import decode_token
from app.schemas.user import UserClaims

app = FastAPI(title="Auth API (no /api/v1 prefix)")

# --- CORS 설정 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 라우터 등록 ---
app.include_router(auth.router)
app.include_router(retrieve.router)
app.include_router(aggregate.router)
app.include_router(compose.router)
app.include_router(uploads.router)

# --- 현재 유저 확인 ---
def get_current_user(authorization: str | None = Header(default=None)) -> UserClaims:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        if payload.get("typ") != "access":
            raise ValueError("Not an access token")
        claims = payload.get("usr") or {}
        return UserClaims(**claims)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --- 내 정보 조회 ---
@app.get("/me")
def read_me(user: UserClaims = Depends(get_current_user)):
    return user
