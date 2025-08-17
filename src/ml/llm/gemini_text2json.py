from google import genai  
from config.settings import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise RuntimeError("환경 변수 GEMINI_API_KEY가 없습니다.")

CategoryEnum = [
    "보석_귀금속_시계",
    "전자기기",
    "문구류",
    "피혁_잡화",
    "기타",
]
ColorEnum = [
    "검정", "검은", "검정색", "흰", "흰색", "파란", "파란색", "빨간", "빨간색",
    "초록", "초록색", "회색", "노란", "노란색", "갈색", "미상"
]

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTIONS = """\
아래 한국어 분실물 설명에서 category, color, raw를 추출하세요.

[카테고리 규칙]
- category는 아래 4개 중 하나를 선택(없거나 불명확하면 "기타")
  1) 보석_귀금속_시계
  2) 전자기기
  3) 문구류
  4) 피혁_잡화
- color는 지정 목록(검정/검은/검정색/흰/흰색/파란/파란색/빨간/빨간색/초록/초록색/회색/노란/노란색/갈색)에서 선택.
  색상 언급이 없으면 "미상".
- raw는 입력 원문 그대로.

[품목→카테고리 힌트(일관성 유지)]
- 보석_귀금속_시계: 반지, 팔찌, 목걸이, 귀걸이, 아날로그손목시계
- 전자기기: 계산기, 마우스, 보조배터리, 무선이어폰, 스마트워치, 무선이어폰크래들, 무선헤드폰, 노트북, 태블릿, 태블릿펜, USB메모리, 휴대폰
- 문구류: 연필, 볼펜, 지우개, 필통, 샤프, 커터칼, 샤프심통, 자
- 피혁_잡화: 지갑, 백팩, 안경, 캡/야구 모자

[출력 형식]
- 반드시 JSON만 출력. 다른 텍스트 금지.
- 필드는 category, color, raw 순서로 배치.
"""

def parse_item_by_genai(text: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # 정밀 우선이면 "gemini-2.5-pro"
        contents=[SYSTEM_INSTRUCTIONS, f"입력: {text}"],
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "category": {
                        "type": "STRING",
                        "enum": [
                            "보석_귀금속_시계",
                            "전자기기",
                            "문구류",
                            "피혁_잡화",
                            "기타",
                        ],
                        "description": "4개 중 최적, 불명확하면 '기타'",
                    },
                    "color": {
                        "type": "STRING",
                        "enum": [
                            "검정","검은","검정색","흰","흰색","파란","파란색",
                            "빨간","빨간색","초록","초록색","회색","노란","노란색",
                            "갈색","미상"
                        ],
                        "description": "색상 언급 없으면 '미상'",
                    },
                    "raw": {
                        "type": "STRING",
                        "description": "입력 원문 그대로",
                    },
                },
                "required": ["category", "color", "raw"],
                "propertyOrdering": ["category", "color", "raw"],
            },
        },
    )

    return " ".join([
        response.parsed.get("category",""), 
        response.parsed.get("color",""), 
        response.parsed.get("raw","")
    ]).strip()