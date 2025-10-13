# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.core.security import decode_token
from app.schemas.user import UserClaims

app = FastAPI(title="Auth API (no /api/v1 prefix)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

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

@app.get("/me")
def read_me(user: UserClaims = Depends(get_current_user)):
    return user
