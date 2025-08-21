#!/usr/bin/env bash
set -euo pipefail

# 인자로 Git SHA를 받습니다. (없으면 latest)
GIT_SHA="${1:-latest}"

# 배포 디렉토리로 이동 (서버에 코드가 클론되어 있다고 가정)
cd ~/app   # 예: /home/ec2-user/app

# 최신 코드 가져오기(서버에 git clone 해뒀다면)
git fetch --all --prune
git checkout main
git pull --ff-only

# Compose 렌더링용 환경변수 주입
export GIT_SHA="$GIT_SHA"

# GHCR 로그인 (토큰은 환경변수 GHCR_TOKEN로 주입)
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

# 최신 이미지 받기 & 컨테이너 롤링
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans

# 마이그레이션/정적파일
docker compose exec -T web python manage.py migrate
docker compose exec -T web python manage.py collectstatic --noinput

# 헬스체크(원하면)
docker compose ps
