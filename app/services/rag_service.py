# app/services/rag_service.py
from typing import List, Dict, Any
from dataclasses import dataclass


from app.core.prompt_loader import load_prompt


# (스텁) 실제 임베딩/검색은 나중에 교체
@dataclass
class Doc:
    doc_id: str
    title: str
    snippet: str
    score: float




def call_llm(system_prompt: str, user_input: str) -> Dict[str, Any]:
    """LLM 호출 스텁. 실제로는 Gemini/GPT SDK로 바꿔주세요."""
    # 예시: retrieve 단계에서는 질의어/필터를 만들어준다 가정
    if "query_terms" in system_prompt or "검색" in system_prompt:
        return {
            "query_terms": [user_input, "불안", "호흡"],
            "filters": {"duration": "<=5m"}
        }
    # aggregate 단계: 문서들을 받아 루틴 스키마로 합친다 가정
    return {
        "situation": {"label": "면접 전 불안", "evidence": []},
        "routine_draft": {
        "title": "3분 복식호흡 루틴",
        "duration_min": 3,
        "steps": ["자세 바로", "4초 들숨", "4초 정지", "4초 날숨 ×4"],
        "why": "호흡 조절은 긴장 완화에 도움"
        }
    }




def retrieve(user_text: str, prompt_name: str = "query_expansion_v1", top_k: int = 5):
    system_prompt = load_prompt("retrieve", prompt_name)
    llm_out = call_llm(system_prompt, user_text)


    # TODO: llm_out을 기반으로 실제 백엔드 검색 로직 연결 (pgvector 등)
    # 여기선 더미 문서 리턴
    docs: List[Doc] = [
        Doc(doc_id="d1", title="복식호흡 4-4-4", snippet="...", score=0.82),
        Doc(doc_id="d2", title="면접 불안 대처", snippet="...", score=0.78),
    ][:top_k]


    return {
        "query": " ".join(llm_out.get("query_terms", [user_text])),
        "filters": llm_out.get("filters", {}),
        "docs": [doc.__dict__ for doc in docs]
    }




def aggregate(retrieved_docs: List[Dict[str, Any]], prompt_name: str = "routine_fusion_v1"):
    # 문서 요약 텍스트로 LLM에 전달하는 형태(간단화)
    docs_text = "\n".join([f"- {d['title']}: {d['snippet']}" for d in retrieved_docs])
    system_prompt = load_prompt("aggregate", prompt_name)
    llm_out = call_llm(system_prompt, docs_text)


    # llm_out에는 situation, routine_draft가 포함되었다고 가정
    return llm_out