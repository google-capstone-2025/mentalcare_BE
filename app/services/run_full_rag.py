import uuid

from app.services.rag_service import retrieve, aggregate
from app.services.compose_service import compose
from app.models import Message, Dedlibered_solutions

def run_full_rag(conversation_id: str, user_msg: str, user_profile: dict, db):

    # 1. RAG 수행   (flag로 추가 정보 필요 유무 구분    1이면 rag재수행  2면 솔루션 정상 제공, 평문 응답 llm)
    retrieved = retrieve(user_msg)
    if (retrieve 실패): # retrieve단계에서 솔루션 vector검색 실패했을 때의 llm 답변 토대로 조건 설정
        return {"msg": "추가정보 필요", "flag": 1} # msg는 임의로 설정함.

    aggregated = aggregate(retrieved["docs"]) #retrieve에서 솔루션 성공하면 
    composed = compose(
        routine_draft=aggregated["routine_draft"],
        user_profile=user_profile
    )

    # 2. LLM 응답 저장 -> 이부분 message테이블에 저장하는 것은 redis로 수정 해야함
    assistant_row = Message(    
        conversation_id=conversation_id,
        role="assistant",
        content=composed["message"]
    )
    db.add(assistant_row)

    # 3. 솔루션 저장    (기존 delibered_solution 삭제 -> 어차피 리포트에 담을건 이러한 솔루션을 했다 정도 이므로 chat_session 테이블에 solution.id 기록해서 참조하는 방식으로?)
    solution_row = Delibered_solutions(
        conversation_id=conversation_id,
        solution_id=aggregated["routine_draft"].get("id", str(uuid.uuid4())) # 원래 이부분에서 routine_draft는 solution이 저장된 테이블에서 벡터 검색하므로 가져올때 solution.id도 가져와서 저장하는 것으로 구상
    )
    db.add(solution_row)
    db.commit()

    # 4. 결과 반환
    return {"result": composed, "flag": 0}