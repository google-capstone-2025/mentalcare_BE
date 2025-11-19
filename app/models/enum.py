# app/models/enum.py
from enum import Enum
from sqlalchemy import Enum as SAEnum

# -----------------------------------
# 기존 Provider, InputType 그대로 유지
# -----------------------------------

class Provider(str, Enum):
    GOOGLE = "google"

ProviderSAEnum = SAEnum(
    Provider,
    name="provider_enum",
    native_enum=True,
    create_type=True,
)

class InputType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"

InputTypeSAEnum = SAEnum(
    InputType,
    name="input_type_enum",
    native_enum=True,
    create_type=True,
)

# -----------------------------------
# NEW: AI 모델 Enum 추가
# -----------------------------------

class AIModel(str, Enum):
    """
    Google Gemini 모델 이름을 관리하는 Enum.
    문자열 오타를 방지하고, 서비스 코드에서 안정적으로 참조하도록 한다.
    """

    #  텍스트 모델
    GEMINI_PRO = "gemini-2.0-pro"
    GEMINI_PRO_EXP = "gemini-2.0-pro-exp"     # 확장(Pro Experimental) 버전
    GEMINI_FLASH = "gemini-2.0-flash"
    GEMINI_FLASH_LITE = "gemini-2.0-flash-lite"

    # 초경량(Nano) 모델
    GEMINI_NANO = "gemini-2.0-nano"
    GEMINI_NANOBANANA = "gemini-2.0-nanobanana"  # 너가 언급한 'nanobanana' 대응

    # 👁 멀티모달 / 이미지 기반 모델
    GEMINI_PRO_VISION = "gemini-2.0-pro-vision"
    GEMINI_FLASH_VISION = "gemini-2.0-flash-vision"

