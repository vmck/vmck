#!/bin/bash -ex

echo "Waiting for Docker..."
until docker version; do sleep 1; done

echo "Waiting for cluster autovault..."
docker exec cluster /bin/bash -c "curl  nomad.service.consul:4646; curl consul.service.consul:8500; ./cluster.py wait"
echo "Cluster provision done."
