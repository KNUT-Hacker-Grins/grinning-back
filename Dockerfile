FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

# mysqlclient 빌드에 필요한 패키지 추가
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --only-binary=:all: -r requirements.txt

COPY . .

CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","1"]