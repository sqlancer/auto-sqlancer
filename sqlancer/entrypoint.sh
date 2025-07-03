#!/bin/bash
echo "=== SQLancer container start ==="

cd /root/sqlancer/target || { echo "Missing target directory"; exit 1; }

# 构造数据库主机名，例如 mysql-8-0
DB_HOST="${DBMS}-${VERSION//./-}"

# 打印命令调试信息
echo "Running: java -jar sqlancer-*.jar --num-threads $SQLANCER_THREADS --timeout-seconds $SQLANCER_TIMEOUT --username $SQLANCER_USERNAME --password $SQLANCER_PASSWORD --host $DB_HOST $DBMS --oracle $SQLANCER_ORACLE"

exec java -jar sqlancer-*.jar \
  --num-threads "$SQLANCER_THREADS" \
  --timeout-seconds "$SQLANCER_TIMEOUT" \
  --username "$SQLANCER_USERNAME" \
  --password "$SQLANCER_PASSWORD" \
  --host "$DB_HOST" \
  "$DBMS" --oracle "$SQLANCER_ORACLE"
