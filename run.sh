#!/bin/bash
set -e

CONFIG_PATH="/root/config.json"
DBMS=$(jq -r '.dbms' "$CONFIG_PATH")

echo "[BOOT] Selected DBMS: $DBMS"

case "$DBMS" in
  mysql)
    bash /root/db_init/start_mysql.sh
    ;;
  postgres)
    bash /root/db_init/start_postgres.sh
    ;;
  *)
    echo "[ERROR] Unsupported DBMS: $DBMS"
    exit 1
    ;;
esac

# 启动 SQLancer 测试
bash /root/sqlancer_runner.sh
