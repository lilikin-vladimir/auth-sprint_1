#!/usr/bin/env bash

./wait-for-it.sh elasticsearch_test:19200 --timeout=60
curl --silent --fail elasticsearch_test:19200/_cluster/health?wait_for_status=green&timeout=60s || exit 1

./wait-for-it.sh redis_test:16379 --timeout=60

exec "$@"
