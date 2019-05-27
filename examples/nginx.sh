#!/bin/bash -ex

docker run --detach --restart always \
  --name vmck-images \
  --volume /opt/volumes/vmck-images:/usr/share/nginx/html:ro \
  --publish 10.66.60.1:9999:80 \
  nginx
