from sqlalchemy import Column, Index, String, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base
from .enum import ModelNameEnum, EmotionEnum, SeverityEnum, InputTypeEnum

class Inferences(Base):
    __tablename__ = "inferences"
    __table_args__ = (Index("idx_inferences_user_time", "user_id", text("created_at DESC")),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    session_id = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    input_id = mapped_column(UUID(as_uuid=True), ForeignKey("inputs.id", ondelete="SET NULL"))
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model = Column(ModelNameEnum, nullable=False)
    emotion_pred = Column(EmotionEnum)
    confidence = Column(Numeric(4, 3))
    signals = Column(JSONB)
    safety_level = Column(SeverityEnum, server_default=text("'low'"))
    retrieved_doc_ids = Column(ARRAY(UUID(as_uuid=True)))
    raw = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    session_id = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(InputTypeEnum, nullable=False)   # assistant/user/system
    content = Column(String, nullable=False)
    card_payload = Column(JSONB)
    model = Column(ModelNameEnum)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
