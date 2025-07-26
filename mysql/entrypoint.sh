#!/bin/bash
set -e

echo "Starting mysqld in background..."
/usr/local/mysql/bin/mysqld --user=mysql --datadir=/var/lib/mysql --basedir=/usr/local/mysql --skip-networking &
pid="$!"

sleep 10

echo "Running init.sql to grant privileges..."
/usr/local/mysql/bin/mysql -uroot < /init.sql

kill "$pid"
sleep 5

echo "Starting MySQL server..."
exec /usr/local/mysql/bin/mysqld --user=mysql --datadir=/var/lib/mysql --basedir=/usr/local/mysql --bind-address=0.0.0.0
