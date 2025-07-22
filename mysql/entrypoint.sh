#!/bin/bash

set -e  

MYSQL_BASEDIR=/usr/local/mysql
MYSQL_DATADIR=$MYSQL_BASEDIR/data

if [ ! -d "$MYSQL_DATADIR/mysql" ]; then
  echo "Initializing MySQL data directory..."
  chown -R mysql:mysql "$MYSQL_BASEDIR"
  mysqld --initialize-insecure --user=mysql --basedir="$MYSQL_BASEDIR" --datadir="$MYSQL_DATADIR"
fi

echo "Starting MySQL server..."
exec mysqld --user=mysql --basedir="$MYSQL_BASEDIR" --datadir="$MYSQL_DATADIR"
