#!/bin/bash
echo "=== SQLancer container start ==="

cd /root/sqlancer/target || { echo "Missing target directory"; exit 1; }

# db_image name
DB_HOST="${DBMS}"

# print test command
echo "Running: java -jar sqlancer-*.jar --num-threads $SQLANCER_THREADS --timeout-seconds $SQLANCER_TIMEOUT --username $SQLANCER_USERNAME --password $SQLANCER_PASSWORD --host $DB_HOST $DBMS --oracle $SQLANCER_ORACLE"

exec java -jar sqlancer-*.jar \
  --num-threads "$SQLANCER_THREADS" \
  --timeout-seconds "$SQLANCER_TIMEOUT" \
  --username "$SQLANCER_USERNAME" \
  --password "$SQLANCER_PASSWORD" \
  --host "$DB_HOST" \
  "$DBMS" --oracle "$SQLANCER_ORACLE"
