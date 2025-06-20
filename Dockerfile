FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV MYSQL_ROOT_PASSWORD=12345678
ENV POSTGRES_PASSWORD=12345678

RUN apt-get update && \
    apt-get install -y default-jdk maven git mysql-server postgresql jq && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/mysqld && chown -R mysql:mysql /var/run/mysqld
RUN mkdir -p /var/run/postgresql && chown -R postgres:postgres /var/run/postgresql

WORKDIR /root

COPY run.sh /root/run.sh
COPY sqlancer_runner.sh /root/sqlancer_runner.sh
COPY run.sql /root/run.sql
COPY config.json /root/config.json
COPY db_init/ /root/db_init/
RUN chmod +x /root/run.sh /root/sqlancer_runner.sh /root/db_init/*.sh

CMD ["/root/run.sh"]
