from .llm.gemini import GeminiService
from .vision.predictor import YOLOManager

def parse_item_by_genai(message: str) -> str:
    return GeminiService.call_gemini_for_parsing_text(message)