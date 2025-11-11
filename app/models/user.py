# app/models/user.py
from sqlalchemy import Column, String, UniqueConstraint, ForeignKey, func, text as sa_text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, CITEXT, TIMESTAMP
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.base_class import Base
from app.models.enum import ProviderSAEnum


class Users(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_text("gen_random_uuid()"),  # ✅ 로그인 시 자동 UUID
        nullable=False,
    )
    # 이메일: 대소문자 구분 없이 유니크, NOT NULL
    email = Column(CITEXT, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    locale = Column(String, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    oauths: Mapped[list["OAuthIdentities"]] = relationship(
        "OAuthIdentities",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class OAuthIdentities(Base):
    __tablename__ = "oauth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_oauth_provider_subject"),
        Index("ix_oauth_identities_user_id", "user_id"),
        Index("ix_oauth_identities_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_text("gen_random_uuid()"),
    )
    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider = Column(ProviderSAEnum, nullable=False)  # enum.py에서 SAEnum 정의 사용
    subject = Column(String, nullable=False)           # OAuth 'sub'
    raw_claims = Column(JSONB)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="oauths",
    )


class TokenRevocations(Base):
    __tablename__ = "token_revocations"
    __table_args__ = (
        Index("ix_token_revocations_user_id", "user_id"),
        Index("ix_token_revocations_revoked_at", "revoked_at"),
    )

    jti = Column(String, primary_key=True)  # JWT ID
    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    reason = Column(String, nullable=True)
    revoked_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
