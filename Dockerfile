FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV MYSQL_VERSION=8.0.36
ENV MYSQL_BASE_URL=https://downloads.mysql.com/archives/get/p/23/file
ENV MYSQL_TAR=mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64.tar.xz

RUN apt-get update && apt-get install -y \
    wget \
    libaio1 \
    libncurses-dev \
    ca-certificates \
    libssl-dev \
    gnupg \
    lsb-release \
    procps \
    xz-utils \
    libnuma1 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt && \
    cd /opt && \
    wget ${MYSQL_BASE_URL}/${MYSQL_TAR} && \
    tar -xf ${MYSQL_TAR} && \
    rm ${MYSQL_TAR} && \
    ln -s /opt/mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64 /usr/local/mysql

RUN groupadd mysql && useradd -r -g mysql mysql && \
    mkdir -p /var/lib/mysql /var/run/mysqld && \
    chown -R mysql:mysql /var/lib/mysql /var/run/mysqld

RUN /usr/local/mysql/bin/mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql

ENV PATH="/usr/local/mysql/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3306
ENTRYPOINT ["/entrypoint.sh"]
