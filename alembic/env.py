# alembic/env.py
from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool
from alembic import context

# ── 1) 프로젝트 루트 경로 추가 (alembic/에서 한 단계 위) ────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ── 2) Base 메타데이터 로드 + 모델 모듈 로드(사이드이펙트로 테이블 등록) ──
from app.db.base_class import Base        # ← Base 선언부 (파일명이 base_class면 여기 맞춰야 함)
import app.models                          # ← 모델들 전부 import되어 Base.metadata에 테이블 등록

# ── 3) Alembic 기본 설정 ────────────────────────────────────────────────
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ── 4) DSN 결정: 환경변수 우선, 없으면 alembic.ini의 sqlalchemy.url ──────
def get_database_url() -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        print(f"[alembic] Using DATABASE_URL: {env_url}")  # 디버그
        return env_url
    ini_url = config.get_main_option("sqlalchemy.url")
    print(f"[alembic] Using ini sqlalchemy.url: {ini_url}")  # 디버그
    return ini_url

# ── 5) 마이그레이션 실행 로직(offline/online) ────────────────────────────
def run_migrations_offline():
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # sqlalchemy.url 대신 우리가 정한 url을 명시적으로 넘김
    connectable = engine_from_config(
        {**config.get_section(config.config_ini_section, {}), "sqlalchemy.url": get_database_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
