from sqlalchemy import Column, String, UniqueConstraint, ForeignKey, func, text as sa_text
from sqlalchemy.dialects.postgresql import UUID, JSONB, CITEXT, TIMESTAMP
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.base_class import Base
from app.models.enum import ProviderEnum

class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_text("gen_random_uuid()"),
    )
    email = Column(CITEXT, unique=True, nullable=True)
    name = Column(String)
    picture_url = Column(String)
    locale = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),  # 선택: 업데이트 시 자동 갱신
    )

    oauths: Mapped[list["OAuthIdentities"]] = relationship(
        "OAuthIdentities",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class OAuthIdentities(Base):
    __tablename__ = "oauth_identities"
    __table_args__ = (UniqueConstraint("provider", "subject", name="uq_oauth_provider_subject"),)

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_text("gen_random_uuid()"),
    )
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(ProviderEnum, nullable=False)
    subject = Column(String, nullable=False)
    raw_claims = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["Users"] = relationship("Users", back_populates="oauths")

class TokenRevocations(Base):
    __tablename__ = "token_revocations"

    jti = Column(String, primary_key=True)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    reason = Column(String)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
