#!/bin/bash
echo "=== SQLancer container start ==="
echo "Waiting for DB to become healthy..."

cd /root/sqlancer/target || { echo "Missing target directory"; exit 1; }

# Wait for the DB container (identified by SQLANCER_HOST) to become healthy
for i in {1..60}; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$SQLANCER_HOST" 2>/dev/null || echo "unknown")
  if [ "$STATUS" = "healthy" ]; then
    break
  fi
  sleep 1
done

echo "[INFO] DB host will be: $SQLANCER_HOST"
echo "Running: java -jar sqlancer-*.jar --num-threads $SQLANCER_THREADS --timeout-seconds $SQLANCER_TIMEOUT --username $SQLANCER_USERNAME --password $SQLANCER_PASSWORD --host $SQLANCER_HOST $SQLANCER_DBMS --oracle $SQLANCER_ORACLE"

exec java -jar sqlancer-*.jar \
  --num-threads "$SQLANCER_THREADS" \
  --timeout-seconds "$SQLANCER_TIMEOUT" \
  --username "$SQLANCER_USERNAME" \
  --password "$SQLANCER_PASSWORD" \
  --host "$SQLANCER_HOST" \
  "$SQLANCER_DBMS" \
  --oracle "$SQLANCER_ORACLE"
