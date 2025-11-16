from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.uploads import UploadTextRequest, UploadResponse
from app.models.input import Inputs
from app.models.enum import InputType  # 🔹 TEXT / IMAGE / AUDIO Enum

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_text(
    payload: UploadTextRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),   # JWT 인증 필수 라우트로 가정
):
    # 1) 텍스트 비어있는지 체크
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")

    # 2) user_id는 inputs.user_id(nullable=False)라서 반드시 필요
    if user is None or getattr(user, "id", None) is None:
        raise HTTPException(status_code=401, detail="unauthorized")

    # 3) Inputs 모델 구조에 맞게 인스턴스 생성
    row = Inputs(
        user_id=user.id,
        session_id=payload.session_id,
        input_type=InputType.TEXT,     # 🔹 enum.py에서 정의한 TEXT 사용
        text_content=payload.text,     # 🔹 content → text_content 로 매핑
        meta=payload.meta or {},
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    # 4) 응답도 input_type 기준으로 통일
    return UploadResponse(
        input_id=row.id,
        session_id=row.session_id,
        input_type=row.input_type.value  # 🔹 InputType.TEXT → "text"
    )


@router.get("/health")
def uploads_health():
    return {"ok": True}
