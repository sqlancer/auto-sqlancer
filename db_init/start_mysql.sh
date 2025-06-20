#!/bin/bash
set -e

echo "[MYSQL] Starting MySQL..."
service mysql start
sleep 10

echo "[MYSQL] Configuring root user authentication..."
mysql -uroot <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '12345678';
FLUSH PRIVILEGES;
EOF

echo "[MYSQL] Running init SQL script..."
mysql -uroot -p12345678 < /root/run.sql || true
