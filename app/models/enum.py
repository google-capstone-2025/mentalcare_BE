from enum import Enum
from sqlalchemy import Enum as PgEnum

# ----- DDL에서 언급된 타입들 -----
# provider, input_channel, input_type, emotion, model_name, severity

class Provider(str, Enum):
    google = "google"
    apple = "apple"
    kakao = "kakao"
    naver = "naver"

class InputChannel(str, Enum):
    text = "text"
    audio = "audio"
    image = "image"
    file = "file"

class InputType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class Emotion(str, Enum):
    calm = "calm"
    happy = "happy"
    sad = "sad"
    angry = "angry"
    anxious = "anxious"
    stressed = "stressed"
    frustrated = "frustrated"
    # 필요 시 추가

class ModelName(str, Enum):
    gemini_flash = "gemini-flash"
    gemini_nano = "gemini-nano"
    # 버전 태그는 raw/jsonB로 보관해도 됨

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

# SQLAlchemy 컬럼에서 재사용할 Enum 팩토리
ProviderEnum = PgEnum(Provider, name="provider", create_type=False)
InputChannelEnum = PgEnum(InputChannel, name="input_channel", create_type=False)
InputTypeEnum = PgEnum(InputType, name="input_type", create_type=False)
EmotionEnum = PgEnum(Emotion, name="emotion", create_type=False)
ModelNameEnum = PgEnum(ModelName, name="model_name", create_type=False)
SeverityEnum = PgEnum(Severity, name="severity", create_type=False)
