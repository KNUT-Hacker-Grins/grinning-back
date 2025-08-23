# Unit6-back

Django 기반 백엔드 서버입니다.  
분실물/습득물 관리, 회원 인증, API 제공 기능을 담당합니다.  
배포는 Docker + docker-compose + Nginx 기반으로 이루어집니다.

---

## 📂 프로젝트 구조

├── .github/workflows/ # CI/CD (GitHub Actions)
├── src/ # Django 프로젝트/앱 소스
│ ├── manage.py
│ └── config/ (settings, urls, wsgi, asgi 등)
├── docker-compose.yml # 로컬 개발용 Compose
├── docker-compose.prod.yml # 운영 환경 Compose
├── Dockerfile # 애플리케이션 Dockerfile
├── nginx.conf # Nginx 설정
├── remote-deploy.sh # 서버 배포 스크립트
├── requirements.txt # 기본 패키지 목록
├── requirements_local.txt # 로컬 개발용 패키지 목록
└── README.md


## 🚀 개발 환경 실행

```bash 
# 가상환경 생성 & 패키지 설치
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_local.txt

# 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```