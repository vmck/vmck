#!/bin/bash -ex

echo "Waiting for Docker..."
until docker version; do sleep 1; done

echo "Waiting for cluster autovault..."
docker exec cluster ./cluster.py wait

echo "Adding vmck_worker meta value..."
sed -i '/nomad_meta/a vmck_worker = true' /opt/cluster/cluster.ini
docker exec cluster ./cluster.py configure
docker exec cluster supervisorctl restart nomad
docker exec cluster ./cluster.py wait

echo "Cluster provision done."
