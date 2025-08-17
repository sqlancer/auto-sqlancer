#!/bin/bash

LOG_DIR="/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/sqlancer.log"

echo "=== SQLancer container start ==="
echo "Waiting for DB to become healthy..."

cd /root/sqlancer/target || { echo "Missing target directory"; exit 1; }

# Wait for the DB container to become healthy
for i in {1..60}; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$SQLANCER_HOST" 2>/dev/null || echo "unknown")
  if [ "$STATUS" = "healthy" ]; then
    break
  fi
  sleep 1
done


CMD="java -jar sqlancer-*.jar --num-threads \"$SQLANCER_THREADS\" --timeout-seconds \"$SQLANCER_TIMEOUT\" --host \"$SQLANCER_HOST\" \"$SQLANCER_DBMS\" --oracle \"$SQLANCER_ORACLE\""


if [ "$(printf '%s' "${SQLANCER_USERNAME:-}" | tr '[:lower:]' '[:upper:]')" != "N/A" ]; then
  CMD="$CMD --username \"$SQLANCER_USERNAME\""
fi


if [ "$(printf '%s' "${SQLANCER_PASSWORD:-}" | tr '[:lower:]' '[:upper:]')" != "N/A" ]; then
  CMD="$CMD --password \"$SQLANCER_PASSWORD\""
fi


echo "Running: $CMD" | tee -a "$LOG_FILE"

eval "$CMD" 2>&1 | tee -a "$LOG_FILE" | grep --line-buffered "Executed"

echo "[INFO] SQLancer finished. Logs saved to $LOG_DIR"
