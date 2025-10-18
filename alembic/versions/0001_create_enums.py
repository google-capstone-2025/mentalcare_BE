# alembic/versions/xxxx_create_enums.py
from alembic import op
import sqlalchemy as sa

revision = "0001_create_enums"
down_revision = None

def upgrade():
    # ENUM 타입 직접 생성
    op.execute("CREATE TYPE emotion AS ENUM ('neutral','calm','happy','proud','grateful','sad','anxious','angry','stressed','lonely','fear','shame');")
    op.execute("CREATE TYPE input_channel AS ENUM ('text','voice','image','system');")
    op.execute("CREATE TYPE input_type AS ENUM ('user','system','assistant');")
    op.execute("CREATE TYPE provider AS ENUM ('google');")
    op.execute("CREATE TYPE model_name AS ENUM ('gemini');")
    op.execute("CREATE TYPE severity AS ENUM ('low','medium','high','critical');")

def downgrade():
    op.execute("DROP TYPE severity;")
    op.execute("DROP TYPE model_name;")
    op.execute("DROP TYPE provider;")
    op.execute("DROP TYPE input_type;")
    op.execute("DROP TYPE input_channel;")
    op.execute("DROP TYPE emotion;")
