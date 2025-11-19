# app/services/inference/base_inference_service.py

import json
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings


class BaseInferenceService:
    """
    모든 inference 서비스(Text, Image, Voice)가 공통으로 사용하는 기반 클래스.
    - Gemini API 호출
    - system_prompt 구성
    - JSON 파싱
    """

    def __init__(self, model_name: Optional[str] = None):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name or settings.GEMINI_MODEL_TEXT  # 기본값: 텍스트용 모델

    # ==============================
    # 공통 System Prompt 생성
    # ==============================
    def build_system_prompt(self) -> str:
        """
        모든 타입(text/image/voice) 공통 감정 분석 규칙.
        JSON 객체만 반환하도록 강하게 요구.
        """
        return (
            "You are an AI assistant that infers human emotions.\n"
            "Read the input (text, image description, or transcribed audio).\n"
            "Output ONLY valid JSON. Nothing outside JSON.\n\n"
            "{\n"
            '  "primary_emotion": "string",\n'
            '  "scores": [ {"emotion": "string", "score": 0.0}, ... ],\n'
            '  "intensity": "low | medium | high",\n'
            '  "explanation": "string"\n'
            "}\n\n"
            "Rules:\n"
            "- Do NOT provide medical or clinical diagnoses.\n"
            "- Focus on everyday emotional state.\n"
            "- Use short, clear explanations.\n"
        )

    # ==============================
    # 구글 Gemini API 호출
    # ==============================
    def call_model(self, user_prompt: str) -> str:
        """
        모델 호출 공통 처리.
        """
        system_prompt = self.build_system_prompt()

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Content(role="system", parts=[types.Part.from_text(system_prompt)]),
                types.Content(role="user", parts=[types.Part.from_text(user_prompt)]),
            ],
        )

        return response.text or ""

    # ==============================
    # JSON 파싱
    # ==============================
    def parse_response(self, raw_text: str) -> Dict[str, Any]:
        """
        모델이 JSON을 반환하도록 프롬프트를 짰지만, 안전하게 파싱.
        """
        try:
            return json.loads(raw_text.strip())
        except json.JSONDecodeError:
            # fallback
            return {
                "primary_emotion": "unknown",
                "scores": [{"emotion": "unknown", "score": 0.0}],
                "intensity": "low",
                "explanation": "Failed to parse model output.",
            }

    # ==============================
    # 타입별 서비스가 override할 메서드
    # ==============================
    def infer(self, *args, **kwargs):
        """
        Text/Image/Voice 서비스에서 override 할 예정.
        """
        raise NotImplementedError("Subclasses must implement the infer() method.")
