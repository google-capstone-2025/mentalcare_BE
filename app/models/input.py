# app/models/input.py
from __future__ import annotations
from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text, func, text as sa_text, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enum import InputTypeSAEnum


class Inputs(Base):
    """
    사용자가 보낸 모든 입력(텍스트, 이미지, 음성 등)을 통합 관리하는 테이블.

    - 초기 단계: 원본 메타데이터 저장 (파일 경로, 업로드 시각 등)
    - 이후 확장: 감정 추론 결과, 처리 상태, AI 분석 메타데이터를 추가 저장
    """

    __tablename__ = "inputs"
    __table_args__ = (
        Index("ix_inputs_user_created_at", "user_id", "created_at"),
        Index("ix_inputs_session_created_at", "session_id", "created_at"),
        Index("ix_inputs_input_type", "input_type"),
    )

    # 기본키
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_text("gen_random_uuid()"),
    )

    # 어떤 사용자의 입력인지
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 세션 식별자 (같은 대화 흐름 구분용)
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 입력 타입 (text / image / audio)
    input_type = Column(InputTypeSAEnum, nullable=False)

    # 업로드 시각
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ====== 원본 데이터 관련 ======
    # 텍스트 입력일 경우 원문 저장
    text_content = Column(Text, nullable=True)

    # 파일 입력일 경우 저장소 정보
    storage_path = Column(String, nullable=True)   # 예: "gs://bucket/2025/11/uuid.png"
    mime_type = Column(String, nullable=True)      # 예: "image/png", "audio/mpeg"
    byte_size = Column(Integer, nullable=True)     # 파일 크기(Byte)

    # ====== 이후 감정추론/AI 분석 결과 (선택적으로 채워짐) ======
    inference_result = Column(JSONB, nullable=True)  # 감정/확신도 등 추론 결과
    meta = Column(JSONB, nullable=True)              # 기타 분석 메타데이터 (ex. 언어, 모델버전 등)

    # 관계 설정
    user = relationship("Users", back_populates="inputs")
    session = relationship("ChatSession", back_populates="inputs")
    # lazy="joined" 등 필요시 옵션 추가 가능

