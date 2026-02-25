#!/bin/sh
set -e

echo "Waiting for Sync Gateway to be ready..."
until wget -qO- http://sync-gateway:4984 > /dev/null 2>&1; do
  echo "Sync Gateway not ready, retrying in 2s..."
  sleep 2
done
echo "Sync Gateway is ready. Starting Edge Server..."

exec couchbase-edge-server --verbose /etc/edge-server/config.json
