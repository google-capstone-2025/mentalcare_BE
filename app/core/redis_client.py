# app/core/redis_client.py
import os
from redis.asyncio import Redis  # asyncio 버전 클라이언트 사용

# Docker 환경에서는 REDIS_URL=redis://redis:6379/0 으로 들어옴
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 전역 Redis 클라이언트 (싱글턴)
redis_client: Redis = Redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,  # str로 주고받게
)
