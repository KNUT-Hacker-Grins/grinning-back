import re
from typing import Dict

COLOR_WORDS = ["검정", "검은", "검정색", "흰", "흰색", "파란", "파란색", "빨간", "빨간색", "초록", "초록색", "회색", "노란", "노란색", "갈색"]
CATEGORY_HINTS = {
    "우산": ["우산"],
    "지갑": ["지갑", "월렛"],
    "휴대폰": ["휴대폰", "핸드폰", "스마트폰", "아이폰", "갤럭시"],
    "필기구": ["연필", "볼펜", "샤프", "펜", "지우개", "자", "커터칼", "샤프심통", "필통"],
    "액세서리": ["반지", "팔찌", "목걸이", "귀걸이", "시계"],
    "전자기기": ["노트북", "태블릿", "태블릿펜", "무선헤드폰", "무선이어폰", "무선이어폰크래들", "보조배터리", "계산기", "마우스", "USB메모리"],
    "가방": ["백팩"],
    "의류": ["모자", "캡", "야구 모자"],
}

def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t

def extract_structured(text: str) -> Dict:
    # 매우 경량 규칙 기반 추출 (초기 MVP)
    raw = text
    text = normalize(text)
    color = ""
    for c in COLOR_WORDS:
        if c in raw:
            color = c
            break
    category = ""
    for k, hints in CATEGORY_HINTS.items():
        if any(h in raw for h in hints):
            category = k
            break
    return {
        "category": category,
        "color": color,
        "raw": raw
    }
