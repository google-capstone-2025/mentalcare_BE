from sqlalchemy import Column, Index, String, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class PromptTemplates(Base):
    __tablename__ = "prompt_templates"
    __table_args__ = (Index("uq_prompt_name_version", "name", "version", unique=True),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    stage = Column(String, nullable=False)        # retrieve/aggregate/compose/guard
    version = Column(Integer, nullable=False, server_default=text("1"))
    locale = Column(String, server_default=text("'ko-KR'"))
    body = Column(String, nullable=False)
    variables = Column(ARRAY(String))
    meta = Column(JSONB)
    is_active = Column(Boolean, nullable=False, server_default=text("FALSE"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
