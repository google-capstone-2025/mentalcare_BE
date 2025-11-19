# app/services/uploads_service.py
# 추후 upload_voice, upload_image 등 다른 업로드 타입이 추가될 것
from typing import Any, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.input import Inputs
from app.models.enum import InputType
from app.schemas.uploads import UploadTextRequest

def create_text_input(
    db: Session,
    user: Any,               # 실제로는 User 모델 타입을 쓰면 더 좋음
    payload: UploadTextRequest,
) -> Inputs:
    """
    사용자가 텍스트를 업로드했을 때 DB에 Inputs 레코드를 생성하는 유즈케이스.
    """

    # 1) 인증/유저 체크 (서비스에서 해도 되고, 라우터에서 미리 걸러도 됨)
    if user is None or getattr(user, "id", None) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
        )

    # 2) 텍스트 검증
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="text is empty",
        )

    # 3) Inputs 인스턴스 생성
    row = Inputs(
        user_id=user.id,
        session_id=payload.session_id,
        input_type=InputType.TEXT,
        text_content=payload.text,
        meta=payload.meta or {},
    )

    # 4) DB 반영
    db.add(row)
    try:
        db.commit()
    except Exception:
        db.rollback()
        # 필요하면 로깅 추가
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to save input",
        )

    db.refresh(row)
    return row
