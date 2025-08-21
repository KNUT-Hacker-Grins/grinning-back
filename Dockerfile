FROM python:3.9-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_ONLY_BINARY=:all: PIP_NO_CACHE_DIR=1 \
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

# 기본 런타임 준비 최소화
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl tini && \
    rm -rf /var/lib/apt/lists/*

# 웹 의존성
COPY requirements.txt .
RUN pip install -r requirements.txt

# (옵션) AI 의존성: ENABLE_AI=1일 때만 설치
ARG ENABLE_AI=0
COPY requirements-ai.txt .
RUN if [ "$ENABLE_AI" = "1" ]; then \
      pip install -r requirements-ai.txt ; \
    fi

# 앱 소스
COPY . .

# 가벼운 서버 설정
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","1"]