# app/routers/uploads.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.uploads import UploadTextRequest, UploadResponse
from app.services.uploads import create_text_input  # 🔹 서비스 레이어 호출

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_text(
    payload: UploadTextRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),   # JWT 인증 필수 라우트
):
    # 비즈니스 로직은 서비스로 분리
    row = create_text_input(db=db, user=user, payload=payload)

    # 응답 스키마 매핑
    return UploadResponse(
        input_id=row.id,
        session_id=row.session_id,
        input_type=row.input_type.value,  # InputType.TEXT -> "text"
    )


@router.get("/health")
def uploads_health():
    return {"ok": True}
