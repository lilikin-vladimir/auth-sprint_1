#!/usr/bin/env bash

./wait-for-it.sh postgres:5432 --timeout=60

./wait-for-it.sh elasticsearch:9200 --timeout=60
curl --silent --fail elasticsearch:9200/_cluster/health?wait_for_status=green&timeout=60s || exit 1

exec "$@"
