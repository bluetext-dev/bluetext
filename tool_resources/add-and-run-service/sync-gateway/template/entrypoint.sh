#!/bin/sh
set -e

# Start Sync Gateway in the background
/entrypoint.sh /etc/sync_gateway/sync-gateway-config.json &
PID=$!

# Wait for Admin API to be available
echo "Waiting for Sync Gateway Admin API..."
until curl -s http://127.0.0.1:4985/ > /dev/null; do
  sleep 2
done

echo "Sync Gateway is up. Configuring database..."

# Create the database (use trailing slash to avoid 301 redirect)
# Use Couchbase credentials for Admin API authentication
curl -v -X PUT http://127.0.0.1:4985/main/ \
  -u asdf:asdfasdf \
  -H "Content-Type: application/json" \
  -d @/etc/sync_gateway/database.json

echo "Database configured."

# Wait for the Sync Gateway process
wait $PID
