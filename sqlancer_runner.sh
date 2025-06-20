#!/bin/bash
set -e

CONFIG_PATH="/root/config.json"
DBMS=$(jq -r '.dbms' "$CONFIG_PATH")
ORACLE=$(jq -r '.oracle' "$CONFIG_PATH")
USERNAME=$(jq -r '.username' "$CONFIG_PATH")
PASSWORD=$(jq -r '.password' "$CONFIG_PATH")
HOST=$(jq -r '.host' "$CONFIG_PATH")
PORT=$(jq -r '.port' "$CONFIG_PATH")
THREADS=$(jq -r '.num_threads' "$CONFIG_PATH")
TIMEOUT=$(jq -r '.timeout_seconds' "$CONFIG_PATH")

echo "[SQLANCER] Cloning SQLancer..."
git clone https://github.com/sqlancer/sqlancer.git
cd sqlancer
mvn package -DskipTests

echo "[SQLANCER] Running test on $DBMS..."
java -jar target/sqlancer-*.jar \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --host "$HOST" \
    --port "$PORT" \
    --num-threads "$THREADS" \
    --timeout-seconds "$TIMEOUT" \
    "$DBMS" --oracle "$ORACLE"
