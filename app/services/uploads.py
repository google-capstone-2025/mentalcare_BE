# app/services/uploads.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.uploads import UploadTextRequest
from app.models.input import Inputs
from app.models.enum import InputType  # TEXT / IMAGE / AUDIO Enum


def create_text_input(
    db: Session,
    user,
    payload: UploadTextRequest,
) -> Inputs:
    """
    텍스트 업로드 비즈니스 로직:
    - 입력값 검증
    - user 검증
    - Inputs row 생성 & 저장
    - 저장된 row 반환
    """

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
        input_type=InputType.TEXT,     # enum TEXT 사용
        text_content=payload.text,
        meta=payload.meta or {},
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return row
