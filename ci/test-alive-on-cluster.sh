#!/usr/bin/env bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

set +e
echo "Starting cluster.py"
python3 /opt/vmck/examples/cluster.py
echo "cluster.py run successfully"

i=0

while [ $i -le 180 ]; do
  if curl --output /dev/null --silent --head --fail "10.66.60.1:9995"; then
    echo "Vmck is up and running"
    exit 0
  else
    sleep 5
    i=$((i + 5))
  fi
done

exit -1
