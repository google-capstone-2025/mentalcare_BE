from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.chat import ChatResponse
from app.models.conversation import Conversation
from app.services.run_full_rag import run_full_rag

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# 채팅 개설을 위한 session_id 리턴 (분석하기 누르면 젤 먼저 실행해서 input테이블의 session_id 설정할 수 있도록) -> conversation테이블 수정해야함
@router.post("", response_model=ChatResponse)
def create_conversation_id(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    
    conv_id = Conversation(user_id = user.id)  
    db.add(conv_id)
    db.commit()
    db.refresh(conv_id) 

    return conv_id

    
# 사용자가 메세지 전송 누를때마다 호출
@router.post("/{conversation_id}/message")
def send_message(
    conversation_id: str,
    user_msg: str,
    flag: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    #사용자 입력 저장 -> 여기도 redis에 저장으로 수정
    row = Message(
        conversation_id = conversation_id,
        role = "user",
        content = user_msg
    )
    db.add(row)
    db.commit()

    # flag 1 이므로 rag 재수행 해야하는 상태 -> 상태제어 flag or llm 선택
    if (flag == 1):
        first_input = ( # 제일 처음 사용자 입력
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .first()
        )
        new_input = first_input.content + " " + user_msg # 첫 입력과 방금 사용자가 보낸 추가 정보 결합
        return run_full_rag(conversation_id, new_input, user.dict(), db)    # rag 재수행
    
    # flag 0 이므로 솔루션 제공 성공 / 단순 위로 or 적절한 대답을 위한 평문 llm 호출
    elif (flag == 0):
        return call_llm(user_msg)
    ''' 추가로 flag 0 이지만 사용자가 다른 솔루션 요청 가능. 
        이 경우 "다른 솔루션" 이라고 사용자가 입력하면 rag 재수행
        (솔루션이 맘에 안들면 "다른 솔루션" 이라고 말해주세요! 라고 고지하는 방식?)
        
        하는 경우도 있을거 같지만 일단 배제'''