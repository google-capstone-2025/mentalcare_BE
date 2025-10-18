from sqlalchemy import Column, Index, String, Integer, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from .enum import EmotionEnum

class Routines(Base):
    __tablename__ = "routines"
    __table_args__ = (Index("idx_routines_user_time", "user_id", text("created_at DESC")),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    session_id = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emotion_target = Column(EmotionEnum)
    title = Column(String, nullable=False)
    summary = Column(String)
    est_minutes = Column(Integer)
    scientific_basis = Column(JSONB)
    source_tags = Column(ARRAY(String))
    accepted = Column(Boolean, server_default=text("FALSE"))
    completed = Column(Boolean, server_default=text("FALSE"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    completed_at = Column(TIMESTAMP(timezone=True))

    steps: Mapped[list["RoutineSteps"]] = relationship("RoutineSteps", back_populates="routine", cascade="all, delete-orphan")

class RoutineSteps(Base):
    __tablename__ = "routine_steps"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    routine_id = mapped_column(UUID(as_uuid=True), ForeignKey("routines.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(Integer, nullable=False)
    instruction = Column(String, nullable=False)
    timer_seconds = Column(Integer)
    checked = Column(Boolean, server_default=text("FALSE"))
    checked_at = Column(TIMESTAMP(timezone=True))

    routine: Mapped["Routines"] = relationship("Routines", back_populates="steps")
