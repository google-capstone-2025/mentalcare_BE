# app/core/revocation.py
from __future__ import annotations
import time
from typing import Dict

# token -> exp(unix)
_revoked: Dict[str, int] = {}

def revoke_refresh(token: str, exp_unix: int | None = None) -> None:
    """해당 refresh 토큰을 만료 시각(exp)까지 블랙리스트로 등록."""
    now = int(time.time())
    # exp가 없으면 30일 기본 보관 (보수적으로)
    ttl = exp_unix if exp_unix and exp_unix > now else now + 30 * 24 * 3600
    _revoked[token] = ttl
    _prune()

def is_refresh_revoked(token: str) -> bool:
    """블랙리스트에 있고 아직 만료 전이면 True."""
    _prune()
    exp = _revoked.get(token)
    if exp is None:
        return False
    return exp > int(time.time())

def _prune() -> None:
    now = int(time.time())
    keys = [k for k, v in _revoked.items() if v <= now]
    for k in keys:
        _revoked.pop(k, None)
