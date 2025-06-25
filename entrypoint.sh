#!/bin/bash
set -e

DBMS="${DBMS:-mysql}"
VERSION="${VERSION:-8.0}"
SQLANCER_THREADS="${SQLANCER_THREADS:-4}"
SQLANCER_TIMEOUT="${SQLANCER_TIMEOUT:-60}"
SQLANCER_ORACLE="${SQLANCER_ORACLE:-FUZZER}"
SQLANCER_USERNAME="${SQLANCER_USERNAME:-root}"
SQLANCER_PASSWORD="${SQLANCER_PASSWORD:-12345678}"

echo "=== [BOOT] Selected DBMS: $DBMS ==="

export PYTHONPATH=/root

# init db
python3 - <<PYCODE
import os
dbms = os.environ["DBMS"]
password = os.environ["SQLANCER_PASSWORD"]
mod = __import__(f"{dbms}.docker_ops", fromlist=["init"])
mod.init(password)
PYCODE

echo "[SQLANCER] Cloning SQLancer..."
git clone https://github.com/sqlancer/sqlancer.git
cd sqlancer
mvn package -DskipTests

echo "[SQLancer] Running test with command:"
echo "java -jar target/sqlancer-*.jar --num-threads $SQLANCER_THREADS --timeout-seconds $SQLANCER_TIMEOUT --username $SQLANCER_USERNAME --password $SQLANCER_PASSWORD $DBMS --oracle $SQLANCER_ORACLE"

java -jar target/sqlancer-*.jar \
  --num-threads "$SQLANCER_THREADS" \
  --timeout-seconds "$SQLANCER_TIMEOUT" \
  --username "$SQLANCER_USERNAME" \
  --password "$SQLANCER_PASSWORD" \
  "$DBMS" \
  --oracle "$SQLANCER_ORACLE"
