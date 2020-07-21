#!/bin/bash

source ../extras/.env

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f pytest/docker/docker-compose.yml \
    --env-file pytest/docker/.env \
    build

if [[ $# -eq 1 ]]; then
  file=$1
else
  file=$@
fi

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f pytest/docker/docker-compose.yml \
    --env-file pytest/docker/.env \
  run --rm \
  --entrypoint="" \
  tests sh -c "pytest --verbose $file"
