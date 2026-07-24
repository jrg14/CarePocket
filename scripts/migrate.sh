#!/usr/bin/env sh

set -eu

docker compose run --rm backend alembic -c alembic.ini upgrade head
