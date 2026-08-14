FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
# src를 모듈 경로에 추가해서 config.wsgi 등을 gunicorn에서 바로 import 가능하게 함
ENV PYTHONPATH=/app/src

# opencv(cv2)가 런타임에 필요로 하는 공유 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/server.txt

COPY . .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]
