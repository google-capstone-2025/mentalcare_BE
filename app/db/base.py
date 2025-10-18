# app/db/base.py
from app.db.base_class import Base
# 아래는 Alembic autogenerate용 사이드이펙트 임포트
from app.models.input import Input  # noqa