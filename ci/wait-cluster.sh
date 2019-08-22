#!/bin/bash -ex

echo "Waiting for Docker..."
until docker version; do sleep 1; done

echo "Waiting for cluster autovault..."
docker exec cluster /bin/bash -c "echo -e '[nomad_meta]\nvolumes=/opt/volumes\n' >> cluster.ini; cat cluster.ini ;./cluster.py wait"
echo "Cluster provision done."
