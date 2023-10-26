#!/usr/bin/env bash

ELASTIC_HOST_CLEAN=${ELASTIC_HOST#http://}
ELASTIC_HOST_CLEAN=${ELASTIC_HOST_CLEAN#https://}

./wait-for-it.sh "${ELASTIC_HOST_CLEAN}:${ELASTIC_PORT}" --timeout=60
curl --silent --fail "${ELASTIC_HOST}:${ELASTIC_PORT}"/_cluster/health?wait_for_status=green&timeout=60s || exit 1

./wait-for-it.sh "${REDIS_HOST}:${REDIS_PORT}" --timeout=60

exec "$@"
