# app/models/input.py
import enum, uuid
from sqlalchemy import Column, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base_class import Base

class Modality(str, enum.Enum):
    text = "text"

class Input(Base):
    __tablename__ = "inputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    modality = Column(SAEnum(Modality, name="modality_enum"), nullable=False, default=Modality.text)
    content = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
