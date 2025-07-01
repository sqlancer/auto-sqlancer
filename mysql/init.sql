-- mysql/init.sql

CREATE DATABASE IF NOT EXISTS test_db;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '12345678';
SELECT host, user FROM mysql.user;
FLUSH PRIVILEGES;
