FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y default-jdk maven git jq curl unzip python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*


# install PostgreSQL 13
RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /root/entrypoint.sh
COPY config.json /root/config.json
COPY postgres /root/postgres
WORKDIR /root
RUN mkdir -p /root/sqlancer && chmod +x /root/entrypoint.sh

COPY postgres/init.sql /db_init/init.sql
RUN chmod 755 /db_init && chmod 644 /db_init/init.sql
CMD ["/root/entrypoint.sh"]
