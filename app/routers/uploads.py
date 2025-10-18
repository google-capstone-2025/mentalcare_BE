from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user  # JWT 가드가 없으면 임시로 주석 처리해도 됨
from app.schemas.uploads import UploadTextRequest, UploadResponse
from app.models.input import Inputs, InputFiles 

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_text(
    payload: UploadTextRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),  # 인증 미구현이면: user=None 로 바꾸고 user_id에 임시값 넣기
):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")

    row = Input(
        user_id=getattr(user, "id", None),  # 임시: 인증 없으면 None 허용하도록 모델 수정 필요
        session_id=payload.session_id,
        modality=Modality.text if hasattr(Modality, "text") else "text",
        content=payload.text,
        meta=payload.meta or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return UploadResponse(
        input_id=row.id,
        session_id=row.session_id,
        modality=row.modality.value if hasattr(row.modality, "value") else row.modality,
    )

# 최소 헬스체크(옵션)
@router.get("/health")
def uploads_health():
    return {"ok": True}
