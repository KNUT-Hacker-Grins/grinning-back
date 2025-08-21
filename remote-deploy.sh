#!/usr/bin/env bash
set -euo pipefail

GIT_SHA="${1:-latest}"
cd ~/app

git fetch --all --prune
git checkout main
git pull --ff-only

export GIT_SHA="$GIT_SHA"

echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

$COMPOSE pull
$COMPOSE up -d --remove-orphans

# web 준비 잠깐 대기 (필요시 healthcheck로 대체)
sleep 8

# 무거운 작업은 메인 컨테이너가 아닌 "임시 컨테이너"에서 수행
$COMPOSE run --rm web python manage.py migrate --noinput
$COMPOSE run --rm web python manage.py collectstatic --noinput

$COMPOSE ps
