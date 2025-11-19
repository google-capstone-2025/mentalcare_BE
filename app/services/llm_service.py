from sqlalchemy.orm import Session
from app.services.chat_service import save_message


def plain_llm(session_id: str, user_msg, db: Session):
    msg = "이거는 평문 llm" # 여기서 msg값에 llm호출 후 결과 반환
    save_message(session_id, "assistant", msg, db)  #llm 답변 저장
    return msg

def summarize_llm():
    pass