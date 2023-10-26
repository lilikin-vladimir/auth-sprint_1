curl -X PUT "localhost:9200/_snapshot/movies_project_backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/tmp/elasticsearch/backup"
  }
}'


curl -X PUT "localhost:9200/_snapshot/movies_project_backup/snapshot_1?wait_for_completion=true"

cd /tmp/elasticsearch
tar czvf backup.tar.gz backup/