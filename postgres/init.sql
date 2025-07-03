-- Sample init SQL for postgres
CREATE DATABASE test;
\connect test
CREATE TABLE t0(c0 SERIAL PRIMARY KEY, c1 TEXT);
INSERT INTO t0(c1) VALUES ('foo'), ('bar');
