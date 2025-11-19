# app/services/inference_text.py
import json
from typing import Dict, Any

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.emotion import (
    EmotionInferenceRequest,
    EmotionInferenceResponse,
    EmotionScore,
)


class EmotionService:
    """
    Google AI(Gemini) API를 이용해서 감정 추론을 수행하는 서비스 레이어.
    """

    def __init__(self):
        # Developer API 사용 (AI Studio에서 발급한 키)
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            # 안정적인 버전만 쓰고 싶으면:
            # http_options=types.HttpOptions(api_version="v1")
        )
        self.model_name = settings.GEMINI_EMOTION_MODEL

    def _build_system_prompt(self) -> str:
        """
        모델에게 감정추론 역할을 설명하는 시스템 프롬프트.
        JSON으로만 응답하게 강하게 요구.
        """
        return (
            "You are an assistant that infers human emotions from short texts.\n"
            "Task:\n"
            "1. Read the user's message.\n"
            "2. Infer likely emotions (e.g., sad, anxious, angry, stressed, calm, happy, etc.).\n"
            "3. Output ONLY valid JSON with the following schema:\n"
            "{\n"
            '  "primary_emotion": "string",\n'
            '  "scores": [\n'
            '    {"emotion": "string", "score": 0.0},\n'
            '    ...\n'
            "  ],\n"
            '  "intensity": "low | medium | high",\n'
            '  "explanation": "short explanation in the user\'s language"\n'
            "}\n"
            "Rules:\n"
            "- Do NOT include any text outside the JSON object.\n"
            "- Do NOT give medical or clinical diagnoses.\n"
            "- Focus on everyday emotional state, not mental disorders.\n"
        )

    def infer(self, body: EmotionInferenceRequest) -> EmotionInferenceResponse:
        """
        실제로 Gemini에게 요청을 보내 감정을 추론하는 핵심 함수.
        """
        system_prompt = self._build_system_prompt()

        # 한국어/영어 같이 섞여도 괜찮게, 간단한 컨텍스트 추가
        user_prompt = (
            f"User language: {body.language}\n"
            f"User message:\n{body.text}"
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Content(
                    role="system",
                    parts=[types.Part.from_text(system_prompt)],
                ),
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(user_prompt)],
                ),
            ],
        )

        raw_text = response.text or ""

        # 모델이 JSON만 내보내도록 프롬프트를 짰지만,
        # 혹시 모르니 앞뒤 공백 제거 후 파싱 시도.
        try:
            data: Dict[str, Any] = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            # JSON 깨지면, 매우 단순한 fallback 로직
            # (프로덕션에서는 로깅 남기고, 기본 구조로 감싸서 반환 등)
            data = {
                "primary_emotion": "unknown",
                "scores": [{"emotion": "unknown", "score": 0.0}],
                "intensity": "low",
                "explanation": "응답을 파싱하는 데 문제가 발생했습니다.",
            }

        # Pydantic에 맞게 매핑
        scores = [
            EmotionScore(
                emotion=item.get("emotion", "unknown"),
                score=float(item.get("score", 0.0)),
            )
            for item in data.get("scores", [])
        ]

        return EmotionInferenceResponse(
            primary_emotion=data.get("primary_emotion", "unknown"),
            scores=scores,
            intensity=data.get("intensity"),
            explanation=data.get("explanation", ""),
            raw_model_output=raw_text,  # 필요 없다면 None으로 바꾸거나 필드 제거해도 됨
        )


# 의존성 주입용 싱글톤 인스턴스
emotion_service = EmotionService()
