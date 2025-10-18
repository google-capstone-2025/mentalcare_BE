# app/services/compose_service.py
from typing import Dict, Any
from app.core.prompt_loader import load_prompt

def compose(routine_draft: Dict[str, Any],
            user_profile: Dict[str, Any] | None = None,
            prompt_name: str = "empathetic_reply_v1") -> Dict[str, Any]:
    """
    compose 단계: routine_draft + user_profile -> 최종 대화 메시지/카드
    """
    system_prompt = load_prompt("compose", prompt_name)

    # TODO: 실제 LLM 호출로 교체
    name = (user_profile or {}).get("name", "사용자")
    steps = ", ".join(routine_draft.get("steps", []))
    message = (
        f"{name}님, 오늘 마음이 많이 지치셨을 수 있어요. "
        f"지금부터 '{routine_draft.get('title','간단 루틴')}'을 함께 해볼까요? "
        f"{steps}. 끝나면 느낌을 한 줄로 남겨주세요."
    )
    return {"message": message, "card": routine_draft}
