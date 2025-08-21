#!/usr/bin/env bash
set -euo pipefail

# 인자로 Git SHA를 받습니다. (없으면 latest)
GIT_SHA="${1:-latest}"

# 배포 디렉토리로 이동
cd ~/app

# 최신 코드 가져오기
git fetch --all --prune
git checkout main
git pull --ff-only

# 환경변수 주입
export GIT_SHA="$GIT_SHA"

# GHCR 로그인
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

# 최신 이미지 받기 & 컨테이너 롤링
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans

# web 컨테이너 준비될 때까지 대기 (예: 10초)
sleep 10

# 마이그레이션/정적파일은 별도 임시 컨테이너에서 실행
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm web python manage.py migrate --noinput
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput

# 상태 확인
docker compose ps
