# app/routers/uploads.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.uploads import UploadTextRequest, UploadResponse
from app.services.upload_text import create_text_input  # 🔹 서비스 임포트

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_text(
    payload: UploadTextRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 실제 로직은 서비스에 위임
    row = create_text_input(db=db, user=user, payload=payload)

    # 서비스는 DB 모델(Inputs)을 반환하고,
    # 라우터는 그걸 응답 스키마(UploadResponse)로 매핑만 해줌
    return UploadResponse(
        input_id=row.id,
        session_id=row.session_id,
        input_type=row.input_type.value,
    )


@router.get("/health")
def uploads_health():
    return {"ok": True}
