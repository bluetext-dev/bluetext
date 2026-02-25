#!/bin/sh
set -e

# Substitute environment variables in config
sed -e "s/\${COUCHBASE_SERVER}/$COUCHBASE_SERVER/g" \
    -e "s/\${COUCHBASE_USERNAME}/$COUCHBASE_USERNAME/g" \
    -e "s/\${COUCHBASE_PASSWORD}/$COUCHBASE_PASSWORD/g" \
    /etc/sync_gateway/sync-gateway-config.json > /tmp/sync-gateway-config.json

# Start Sync Gateway in the background
/entrypoint.sh /tmp/sync-gateway-config.json &
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
  -u "${COUCHBASE_USERNAME}:${COUCHBASE_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d @/etc/sync_gateway/database.json

echo "Database configured."

# Wait for the Sync Gateway process
wait $PID
