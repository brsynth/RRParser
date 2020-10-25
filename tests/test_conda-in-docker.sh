#!/bin/bash

source ../extras/.env

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f conda/docker/docker-compose.yml \
    --env-file conda/docker/.env \
    build

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f conda/docker/docker-compose.yml \
    --env-file conda/docker/.env \
  run --rm \
  build

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f conda/docker/docker-compose.yml \
    --env-file conda/docker/.env \
  run --rm \
  test
