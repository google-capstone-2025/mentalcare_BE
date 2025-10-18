# Import all models here so Alembic 'autogenerate' sees them
from app.db.base_class import Base

# enums 먼저
from app.models.enum import *  # noqa

# IAM
from app.models.user import Users, OAuthIdentities, TokenRevocations  # noqa

# 입력력
from app.models.input import Inputs, InputFiles  # noqa

# 추론
from app.models.inference import Inferences, Messages  # noqa

# 세션
from app.models.session import ChatSessions  # noqa

# 루틴
from app.models.routine import Routines, RoutineSteps  # noqa

# 프롬프트 템플릿
from app.models.prompt_template import PromptTemplates  # noqa



