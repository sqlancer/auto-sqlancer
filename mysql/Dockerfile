FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y wget libaio1 libncurses6 libnuma1 xz-utils pwgen lsb-release gnupg libssl-dev && \
    apt-get clean

ENV MYSQL_VERSION=8.3.0 \
    MYSQL_USER=mysql \
    MYSQL_BASE=/usr/local/mysql \
    MYSQL_DATADIR=/var/lib/mysql

RUN wget https://downloads.mysql.com/archives/get/p/23/file/mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64.tar.xz && \
    tar -xf mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64.tar.xz && \
    mv mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64 ${MYSQL_BASE} && \
    rm mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64.tar.xz

RUN useradd -r -s /bin/false ${MYSQL_USER} && \
    mkdir -p ${MYSQL_DATADIR} /var/run/mysqld && \
    chown -R ${MYSQL_USER}:${MYSQL_USER} ${MYSQL_DATADIR} /var/run/mysqld ${MYSQL_BASE}

RUN ${MYSQL_BASE}/bin/mysqld --initialize-insecure --basedir=${MYSQL_BASE} --datadir=${MYSQL_DATADIR} --user=${MYSQL_USER}

COPY init.sql /init.sql

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH=${MYSQL_BASE}/bin:$PATH

EXPOSE 3306

ENTRYPOINT ["/entrypoint.sh"]
