#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

set -e

python3 /opt/vmck/examples/cluster.py

i=0

while [ $i -le 180 ]; do
  if curl --output /dev/null --silent --head --fail "10.66.60.1:9995"; then
    exit 0
  else
    sleep 5
    i=$((i + 5))
  fi
done

exit 1
