# 파일: services/gemini_service.py
import json
from typing import Any, Dict
import google.generativeai as genai
from config.settings import GEMINI_API_KEY
from .prompt import (
    prompt_for_category,
    config_for_category,
    prompt_for_translating,
    config_for_translating,
    prompt_for_auto_posting,
    config_for_auto_posting,
)

class GeminiService:
    _model = None  # class-level singleton

    @classmethod
    def _get_model(cls):
        if not GEMINI_API_KEY:
            raise RuntimeError("환경 변수 GEMINI_API_KEY가 없습니다.")
        if cls._model is None:
            genai.configure(api_key=GEMINI_API_KEY)
            cls._model = genai.GenerativeModel("gemini-2.5-flash")
        return cls._model

    @classmethod
    def call_gemini(cls, message: str, custom_prompt: str, custom_config: dict) -> Dict[str, Any]:
        model = cls._get_model()
        resp = model.generate_content(
            contents=[custom_prompt, f"입력: {message}"],
            generation_config=custom_config,
        )

        # schema가 적용되면 parsed 사용
        if hasattr(resp, "parsed") and resp.parsed is not None:
            return resp.parsed

        # 폴백: 원시 응답에서 JSON 텍스트 추출
        raw = resp.to_dict()
        try:
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Gemini 응답 JSON 파싱 실패: {e}. raw={raw}")

    @classmethod
    def call_gemini_for_parsing_text(cls, message: str) -> str:
        data = cls.call_gemini(message, prompt_for_category, config_for_category)
        return cls.transform_json2txt_for_gemini(data)

    @classmethod
    def call_gemini_for_auto_posting(cls, message: str):
        return cls.call_gemini(message, prompt_for_auto_posting, config_for_auto_posting)

    @staticmethod
    def transform_json2txt_for_gemini(dic: Dict[str, Any]) -> str:
        return " ".join([
            str(dic.get("category", "")).strip(),
            str(dic.get("color", "")).strip(),
            str(dic.get("raw", "")).strip(),
        ]).strip()
