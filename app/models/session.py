# app/models/session.py
from sqlalchemy import Column, String, ForeignKey, func, Index, text as sa_text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class ChatSessions(Base):
    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("idx_chat_sessions_user_time", "user_id", sa_text("started_at DESC")),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=sa_text("gen_random_uuid()"),
    )
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    goal = Column(String)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    ended_at = Column(TIMESTAMP(timezone=True))
    meta = Column(JSONB)

    inputs: Mapped[list["Inputs"]] = relationship("Inputs", back_populates="session", cascade="all, delete-orphan")
