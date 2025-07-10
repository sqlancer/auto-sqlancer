#!/bin/bash
echo "=== SQLancer container start ==="
echo "Waiting for DB to become healthy..."

cd /root/sqlancer/target || { echo "Missing target directory"; exit 1; }

# db_image name
DB_HOST="${DBMS}"


# healthy check
for svc in $SQLANCER_HOST; do
  for i in {1..60}; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$svc" 2>/dev/null || echo "unknown")
    echo "Health status of $svc: $STATUS"
    if [ "$STATUS" = "healthy" ]; then
      break
    fi
    sleep 1
  done
done

echo "Running: java -jar sqlancer-*.jar --num-threads $SQLANCER_THREADS --timeout-seconds $SQLANCER_TIMEOUT --username $SQLANCER_USERNAME --password $SQLANCER_PASSWORD --host $SQLANCER_HOST $SQLANCER_DBMS --oracle $SQLANCER_ORACLE"

exec java -jar sqlancer-*.jar \
  --num-threads "$SQLANCER_THREADS" \
  --timeout-seconds "$SQLANCER_TIMEOUT" \
  --username "$SQLANCER_USERNAME" \
  --password "$SQLANCER_PASSWORD" \
  --host "$SQLANCER_HOST" \
  "$SQLANCER_DBMS" \
  --oracle "$SQLANCER_ORACLE"
