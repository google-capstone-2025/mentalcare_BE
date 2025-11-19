import uuid
import json

from app.services.rag_service import retrieve, aggregate
from app.services.compose_service import compose
from app.services.llm_service import summarize_llm
from app.models import Inputs
from redis import Redis
from sqlalchemy.orm import Session


redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)

def run_full_rag(session_id: str, user_msg: str, user_profile: dict, db: Session):

    # 1. RAG 수행   (flag로 추가 정보 필요 유무 구분    1이면 rag재수행  2면 솔루션 정상 제공, 평문 응답 llm)
    retrieved = retrieve(user_msg)
    if (retrieve 실패): # retrieve단계에서 솔루션 vector검색 실패했을 때의 llm 답변 토대로 조건 설정
        return {"msg": "추가정보 필요", "flag": 1} # msg는 임의로 설정함.

    aggregated = aggregate(retrieved["docs"]) #retrieve에서 솔루션 성공하면 
    composed = compose(
        routine_draft=aggregated["routine_draft"],
        user_profile=user_profile
    )

    # 2. LLM 응답 저장 
    save_message(session_id, "assistant", composed["message"], db)

    # 3. 솔루션 저장    (기존 delibered_solution 삭제 -> 어차피 리포트에 담을건 이러한 솔루션을 했다 정도 이므로 chat_session 테이블에 solution.id 기록해서 참조하는 방식으로?)
    solution_row = Delibered_solutions(
        conversation_id=conversation_id,
        solution_id=aggregated["routine_draft"].get("id", str(uuid.uuid4())) # 원래 이부분에서 routine_draft는 solution이 저장된 테이블에서 벡터 검색하므로 가져올때 solution.id도 가져와서 저장하는 것으로 구상
    )
    db.add(solution_row)
    db.commit()

    # 4. 결과 반환
    return {"result": composed, "flag": 0}



# 메시지 redis 저장
def save_message(session_id: str, role: str, content: str, db: Session):
    
    key_msg = f"session:messages:{session_id}"  # 원문 저장용
    message = {
        "role": role,
        "content": content,
    }
    
    redis_client.rpush(key_msg, json.dumps(message, ensure_ascii=False))

    # redis에 저장된 메세지가 6개면 중간 요약 수행
    count = redis_client.llen(key_msg)
    if (count % 6 == 0):
        summarize_message(session_id, key_msg, db)


# 메세지 요약
def summarize_message(session_id: str, key_msg, db: Session):

    key_idx = f"session:summary_index:{session_id}" # 마지막으로 요약된 메세지 index
    key_sum = f"session:summary:{session_id}"       # 요약 결과 저장용

    count = redis_client.llen(key_msg)
    last_idx = int(redis_client.get(key_idx)) if redis_client.get(key_idx) else -1

    messages = redis_client.lrange(key_msg, last_idx+1, count-1)
    msgs = [json.loads(m) for m in messages]

    
    if (last_idx == -1):
        '''
        요약된 메세지가 하나도 없을 때 (첫 요약)
        inputs 에서 첫 text 입력을 포함하여 메세지 요약 실행
        '''
        row = (
            db.query(Inputs)
            .filter(Inputs.session_id == session_id)
            .one()
        )
        first_input = row.text_content
        new_summary = summarize_llm(first_input, msgs)
      
    else:
        '''
        요약된 메세지가 하나도 없을 때 (첫 요약)
        inputs 에서 첫 text 입력을 포함하여 메세지 요약 실행
        '''
        prev_summary = redis_client.get(key_sum) or ""
        new_summary = summarize_llm(prev_summary, msgs)

    redis_client.set(key_sum, new_summary)
    redis_client.set(key_idx, count - 1)
    


# 원문 메세지 전부 가져오기
def get_all_messages(session_id: str):
    key = f"session:messages:{session_id}"
    raw_list = redis_client.lrange(key, 0, -1)

    return [json.loads(item) for item in raw_list]



# 요약문 가져오기
def get_sum_messages(session_id: str):
    key_sum = f"session:summary:{session_id}"
    raw = redis_client.get(key_sum)

    return json.loads(raw) if raw else None

# 채팅 종료 누르면 요약 1번더, gcs 업로드
# llm을 이용한 요약 생성
# gcs 업로드를 위한 get all messages로 가져와서 업로드
# key_sum 내용은 세션 리포트에 활용
# 위 내용 구현 해야함...