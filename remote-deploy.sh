#!/usr/bin/env bash
set -euo pipefail

# 0) 인자 없으면 latest
GIT_SHA="${1:-latest}"

cd ~/app
git fetch --all --prune
git checkout main
git pull --ff-only

# 1) 필요 환경변수 확인(없으면 즉시 실패해 원인 명확화)
: "${GHCR_TOKEN:?GHCR_TOKEN not set}"
: "${GHCR_USER:?GHCR_USER not set}"

echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

# 2) compose 파일 경로
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

# 3) GIT_SHA를 compose에 ‘값’으로 주입해 치환 문제 원천 차단
#    (env 로 넘기는 대신 inline로 넘겨서 다른 변수들과 섞여 오염될 여지 제거)
GIT_SHA_VAL="$GIT_SHA" \
$COMPOSE pull

GIT_SHA_VAL="$GIT_SHA" \
$COMPOSE up -d --remove-orphans

# 4) (선택) DB 준비 시간 확보. healthcheck가 있다면 줄여도 됨
sleep 5

# 5) 관리 작업은 exec로(메모리/환경 일치 장점). run을 꼭 써야 하면 그대로 두셔도 됩니다.
GIT_SHA_VAL="$GIT_SHA" \
$COMPOSE exec -T web python manage.py migrate --noinput

GIT_SHA_VAL="$GIT_SHA" \
$COMPOSE exec -T web python manage.py collectstatic --noinput

$COMPOSE ps
