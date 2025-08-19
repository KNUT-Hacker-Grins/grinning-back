import google.generativeai as genai
from config.settings import GEMINI_API_KEY
from .prompt import *

class GeminiService:
    
    _model = None

    def __init__(self):
        if not GEMINI_API_KEY:
            raise RuntimeError("환경 변수 GEMINI_API_KEY가 없습니다.")

        if not self._model:
            genai.configure(api_key=GEMINI_API_KEY)
            self._model = genai.GenerativeModel('gemini-2.5-flash')

    def call_gemini(self, message, custom_prompt, custom_config):
        response = self._model.generate_content(
            contents=[custom_prompt, f"입력: {message}"],
            generation_config=custom_config
        )
        return self.transform_json2txt_for_gemini(response.to_dict())
    
    @classmethod
    def call_gemini_for_parsing_text(cls, message: str) -> str:
        return cls.call_gemini(message, prompt_for_category, config_for_category)

    @classmethod
    def call_gemini_for_translating(cls, message: str) -> str:
        return cls.call_gemini(message, prompt_for_translating, config_for_translating)

    @classmethod
    def call_gemini_for_auto_posting(cls, message: str) -> str:
        return cls.call_gemini(message, prompt_for_auto_posting, config_for_auto_posting)

    @staticmethod
    def transform_json2txt_for_gemini(dic: dict):
        return " ".join([dic.get("category",""), dic.get("color",""), dic.get("raw","")]).strip()
