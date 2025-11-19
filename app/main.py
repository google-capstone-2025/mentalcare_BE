# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, retrieve, aggregate, compose, uploads
from app.core.security import decode_token
from app.schemas.user import UserClaims
from app.core.redis_client import redis_client

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

@app.on_event("startup")
async def on_startup():
    # 앱이 뜰 때 Redis에 실제로 붙어보며 연결 확인
    try:
        pong = await redis_client.ping()
        print("✅ Redis connected. PING:", pong)
    except Exception as e:
        # 운영 환경에서는 로거 사용 권장
        print("❌ Redis connection failed:", repr(e))

@app.on_event("shutdown")
async def on_shutdown():
    # 이벤트 루프가 내려갈 때 연결 정리
    try:
        await redis_client.close()
        print("🔌 Redis connection closed.")
    except Exception:
        pass

@app.get("/cache")
async def cache_example():
    # = 값 넣고/읽고/TTL 주기
    await redis_client.set("hello", "world", ex=60)
    return {
        "hello": await redis_client.get("hello"),
        "ttl": await redis_client.ttl("hello"),
    }