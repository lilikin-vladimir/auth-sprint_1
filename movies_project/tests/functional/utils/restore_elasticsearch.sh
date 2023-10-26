#!/usr/bin/env bash
set -e

rm -rf /tmp/elasticsearch/backup
mkdir -p /tmp/elasticsearch/backup
tar xzvf /tmp/elasticsearch/backup.tar.gz -C /tmp/elasticsearch

curl -X PUT "elasticsearch_test:19200/_snapshot/movies_project_backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/tmp/elasticsearch/backup"
  }
}'

curl -X POST "elasticsearch_test:19200/_snapshot/movies_project_backup/snapshot_1/_restore"
