# Grinning (그리닝)

유실물 플랫폼 **그리닝의 Django 백엔드**입니다. 분실물·습득물 게시판, 사진 분류, 유사 게시글 추천, 사용자 간 채팅 API를 제공하고, 경찰청 유실물 데이터를 수집해 함께 조회합니다. 화면은 [grinning-front](https://github.com/KNUT-Hacker-Grins/grinning-front)에서 개발합니다.

![그리닝 서비스 소개와 로그인·홈 화면](docs/images/img.png)

## 💡 개발 배경 (Why?)
- **파편화된 정보의 통합:** 분실물 정보가 경찰청, 개별 업체, 지역 커뮤니티마다 흩어져 있어 사용자가 어디서 물건을 찾아야 할지 모르는 불편함을 해소하고자 했습니다.
- **데이터 허브 구축:** 경찰청 유실물 API 데이터와 사용자가 직접 등록한 습득물 정보를 한데 모아, 단 한 곳에서 모든 분실물 정보를 확인할 수 있는 통합 검색 환경을 제공합니다.
- **지능형 양방향 매칭:** 단순히 정보를 나열하는 것에 그치지 않고, 내가 잃어버린 물건을 찾아달라는 게시물과 실제 습득된 정보를 AI가 분석하여 주인에게 연결해주는 능동적인 반환 시스템을 목표로 합니다.
- **분류 및 등록 자동화:** 정보 통합 과정에서 발생하는 대량의 데이터를 AI(YOLOv8)가 자동으로 분류하여 사용자와 관리자의 등록 번거로움을 획기적으로 줄였습니다.

![기존 유실물 시스템의 불편함과 통합 서비스 구상](docs/images/img_1.png)

## 📸 화면별 이미지

![홈 화면, AI 챗봇 화면, 사용자 간 채팅 화면](docs/images/img_2.png)
![사진 분류 결과, 물품 등록 화면, 게시글 상세 화면](docs/images/img_3.png)

## 시작하기

Python 3.12가 필요합니다. Linux에서는 OpenCV용 `libgl1`, `libglib2.0-0`도 설치되어 있어야 합니다.

저장소 루트에서 실행합니다. 예제 설정을 복사하고 DB를 SQLite로 지정해, 외부 서비스 호출 없이 상태 API를 확인하는 로컬 실행 경로입니다.

```sh
python -m pip install -r requirements/server.txt
cp .env.example .env
export DATABASE_URL=sqlite:///db.sqlite3
python src/main.py makemigrations accounts messaging chatbot questionnaire found_items lost_items reports lost_insight police
python src/main.py migrate
python src/main.py runserver
```

실행 후 `http://127.0.0.1:8000/api/chatbot/health`에 접속해 `ok`, `state`, `session_id`가 포함된 JSON 응답을 확인합니다.

## 관련 문서

- [YOLO 모델 학습 환경](src/ml/vision/readme.md)

## 라이선스

LICENSE 파일이 없습니다. 라이선스는 확인이 필요합니다.
