# app/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional

class UserClaims(BaseModel):
    sub: str = Field(..., description="사용자 고유 식별자 (JWT의 sub)")
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    # 필요 시 추가: iss, aud, iat, exp 등

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
