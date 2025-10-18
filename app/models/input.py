from sqlalchemy import Column, Index, String, Integer, ForeignKey, text as sa_text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from .enum import InputChannelEnum, InputTypeEnum, EmotionEnum

class Inputs(Base):
    __tablename__ = "inputs"
    __table_args__ = (
        Index("idx_inputs_session_time", "session_id", "created_at"),
        Index("idx_inputs_user_time", "user_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("gen_random_uuid()"))
    session_id = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel = Column(InputChannelEnum, nullable=False)
    role = Column(InputTypeEnum, nullable=False)
    text = Column(String)
    lang = Column(String)
    emotion_hint = Column(EmotionEnum)
    meta = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    session: Mapped["ChatSessions"] = relationship("ChatSessions", back_populates="inputs")
    files: Mapped[list["InputFiles"]] = relationship("InputFiles", back_populates="input", cascade="all, delete-orphan")

class InputFiles(Base):
    __tablename__ = "input_files"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("gen_random_uuid()"))
    input_id = mapped_column(UUID(as_uuid=True), ForeignKey("inputs.id", ondelete="CASCADE"), nullable=False)
    kind = Column(String, nullable=False)         # "audio","image","pdf"
    storage_uri = Column(String, nullable=False)  # gs:// or s3://
    mime_type = Column(String)
    bytes = Column(Integer)
    meta = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    input: Mapped["Inputs"] = relationship("Inputs", back_populates="files")
