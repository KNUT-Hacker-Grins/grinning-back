prompt_for_category = """\
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

config_for_category ={
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
  }
}

prompt_for_auto_posting = """\
아래는 한국어로 작성된 분실물/습득물 설명입니다. 설명을 읽고 지정된 스키마에 맞춰 JSON만 출력하세요.
불필요한 텍스트는 절대 출력하지 마세요(코멘트/해설/마크다운 금지). 

[필드 설명]
- title: 최대 100자. 핵심만 요약하여 사람이 바로 볼 수 있는 제목 생성.
  - 형식 권장: "[분실] {핵심품목/색상} - {장소(요약)} ({시각 요약})" 또는 "[습득] …"
  - 시각/장소가 불명확하면 생략 가능.
- description: 입력 원문을 간결히 정리(핵심 정보 유지, 불필요한 군더더기 제거). 
- category: 아래 5개 중 하나를 선택(불명확하면 "기타")
    1) 보석_귀금속_시계
    2) 전자기기
    3) 문구류
    4) 피혁_잡화
    5) 기타
- color: 아래 목록에서만 선택. 언급 없거나 애매하면 "unknown".
  ["검정","검은","검정색","흰","흰색","파란","파란색","빨간","빨간색",
   "초록","초록색","회색","노란","노란색","갈색","unknown"]
  - 색상 표준화 규칙(예): '빨강','레드' → '빨간색', '블루' → '파란색', '블랙' → '검정색' 등 가장 가까운 항목으로 매핑.
- latitude, longitude: 텍스트에 좌표가 명시된 경우만 추출(소수점 6자리 이내). 없으면 null.
- found_at: 습득(=주웠다) 시점이 명확하면 ISO 8601(예: "2025-08-18T20:00:00+09:00"). 
  - 분실(=잃어버렸다)만 언급된 경우 null.
- found_location: 습득 장소(자연어). 분실만 언급되거나 모호하면 빈 문자열 "".

[추가 규칙]
- 입력이 '분실' 상황이면 found_at=null, found_location="" 로 둔다.
- 입력이 '습득' 상황이면 가능하면 found_at/ found_location을 채운다.
- title은 100자 이내, color는 지정된 목록으로만.
- 좌표 추정/지오코딩 금지(명시되지 않으면 latitude/longitude는 null).
- 어제 또는 그제 등 때를 나타내는 부사가 문장에 있을 경우 그날의 날짜를 생각해서 found_at 넣도록 참고.

[출력 형식]
아래 스키마에 정확히 맞는 JSON만 출력:
{
  "title": string,
  "description": string,
  "category": "보석_귀금속_시계" | "전자기기" | "문구류" | "피혁_잡화" | "기타",
  "color": "검정" | "검은" | "검정색" | "흰" | "흰색" | "파란" | "파란색" | "빨간" | "빨간색" | "초록" | "초록색" | "회색" | "노란" | "노란색" | "갈색" | "미상",
  "latitude": number|null,
  "longitude": number|null,
  "found_at": string|null,
  "found_location": string
}

[예시]
입력:
"8월 20일 저녁 8시 경에 서울시립도서관 1층에서 빨간색 가죽지갑을 습득함"

정답 예시(JSON만):
{
  "title": "[습득] 빨간색 가죽지갑 - 서울시립도서관 1층 (어제 20:00)",
  "description": "20일 20시경 서울시립도서관 1층에서 빨간색 가죽 지갑을 습득했습니다.",
  "category": "피혁_잡화"
  "color": "빨간색",
  "latitude": null,
  "longitude": null,
  "found_at": "2025-08-20T20:00:00",
  "found_location": "서울시립도서관 1층"
}

[예시]
입력:
"8월 20일 저녁 8시 경에 서울시립도서관 1층에서 빨간색 가죽지갑을 분실함"

정답 예시(JSON만):
{
  "title": "[분실] 빨간색 가죽지갑 - 서울시립도서관 1층 (어제 20:00)",
  "description": "20일 20시경 서울시립도서관 1층에서 빨간색 가죽 지갑을 분실했습니다.",
  "category": "피혁_잡화"
  "color": "빨간색",
  "latitude": null,
  "longitude": null,
  "found_at": "2025-08-20T20:00:00",
  "found_location": "서울시립도서관 1층"
}
"""


config_for_auto_posting = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "properties": {
            "title": { "type": "STRING", "description": "<=100자 요약 제목" },
            "description": { "type": "STRING", "description": "핵심만 정리한 설명" },
             "category": {
                "type": "STRING",
                "enum": ["보석_귀금속_시계", "전자기기", "문구류", "피혁_잡화", "기타"]
            },
            "color": {
                "type": "STRING",
                "enum": [
                    "검정","검은","검정색","흰","흰색","파란","파란색",
                    "빨간","빨간색","초록","초록색","회색","노란","노란색",
                    "갈색","unknown"
                ]
            },
            "latitude": { "type": "NUMBER", "nullable": True, "description": "소수 6자리 이내" },
            "longitude": { "type": "NUMBER", "nullable": True, "description": "소수 6자리 이내" },
            "found_at": { "type": "STRING", "nullable": True, "description": "ISO8601 혹은 null" },
            "found_location": { "type": "STRING", "description": "습득 장소. 없으면 빈 문자열" }
        },
        "required": ["title","description","category","color","latitude","longitude","found_at","found_location"],
        "propertyOrdering": ["title","description","category","color","latitude","longitude","found_at","found_location"]
    }
}


