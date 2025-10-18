from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID

class UploadTextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    session_id: Optional[UUID] = None
    meta: Optional[Dict] = None

class UploadResponse(BaseModel):
    input_id: UUID
    session_id: Optional[UUID]
    modality: str
