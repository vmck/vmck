#!/bin/bash -ex

docker run --detach --restart always \
  --name vmck \
  --volume /opt/volumes/vmck/data:/opt/vmck/data \
  --env SECRET_KEY=foo \
  --env HOSTNAME='*' \
  --env CONSUL_URL=http://10.66.60.1:8500 \
  --env NOMAD_URL=http://10.66.60.1:4646 \
  --env DEBUG=true \
  --env BACKEND=qemu \
  --env QEMU_IMAGE_URL=http://10.66.60.1:9999/bionic-vagrant.qcow2 \
  --publish 10.66.60.1:8000:8000 \
  $(docker build . -q)
