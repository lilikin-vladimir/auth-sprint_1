#!/usr/bin/env bash
set -e

/app/restore_elasticsearch.sh

# Выполнение команд, переданных в параметр 'command' в docker-compose
exec "$@"
