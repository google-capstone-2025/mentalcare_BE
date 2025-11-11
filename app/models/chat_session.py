from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ChatSession(Base):
    """
    한 번의 대화 흐름(세션)을 표현하는 최소 테이블.
    - id: 세션 고유 ID (session_id 역할)
    - user_id: 사용자 UUID
    - message_ref_id: (옵션) 세션을 트리거한 원문 메시지/입력의 참조 ID
    - start_time: 세션 시작 시각
    """

    __tablename__ = "chat_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),   # PostgreSQL: gen_random_uuid()
        comment="세션 고유 ID"
    )

    # NOTE: users 테이블이 없다면 FK는 잠시 주석처리하거나 nullable=True로만 두세요.
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="세션 소유 사용자 UUID"
    )

    # 세션을 시작시킨 원문 메시지/입력의 ID(필요 시 사용). 외래키 강제는 하지 않음.
    message_ref_id = Column(
        UUID(as_uuid=True),
        nullable=True,      #나중에 massage 테이블이 생기면 ForeignKey로 연결 가능 그때 false로 변경
        comment="세션의 원문 메시지/입력 참조 ID(옵션)"
    )

    start_time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="세션 시작 시각"
    )

    # 관계: Input만 연결(선택). 필요 없으면 아래 4줄을 삭제해도 동작합니다.
    inputs = relationship(
        "Input",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    session_report = relationship("SessionReport",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan"
        )

    def __repr__(self):
        return f"<ChatSession id={self.id} user={self.user_id} start={self.start_time}>"
