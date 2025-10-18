# app/routers/compose.py
from fastapi import APIRouter
from app.schemas.compose import ComposeRequest, ComposeResponse
import app.services.compose_service as compose_service  # ← 변경 포인트

router = APIRouter(prefix="/api/compose", tags=["RAG-Compose"])

@router.post("", response_model=ComposeResponse)
def run_compose(payload: ComposeRequest):
    return compose_service.compose(   # ← 모듈.함수 형태로 호출
        routine_draft=payload.routine_draft,
        user_profile=payload.user_profile
    )
