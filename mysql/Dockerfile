FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git cmake make gcc g++ bison \
    libncurses5-dev libssl-dev libaio-dev \
    libz-dev libsystemd-dev \
    perl wget curl vim pkg-config \
    && apt-get clean

WORKDIR /root
RUN git clone https://github.com/mysql/mysql-server.git
WORKDIR /root/mysql-server
RUN git checkout 8.4
RUN mkdir bld
WORKDIR /root/mysql-server/bld
RUN cmake .. \
  -DDOWNLOAD_BOOST=1 \
  -DWITH_BOOST=../boost \
  -DCMAKE_INSTALL_PREFIX=/usr/local/mysql \
  -DWITH_SSL=system \
  -DWITH_ZLIB=bundled \
  -DWITH_INNODB_MEMCACHED=OFF \
  -DENABLE_DOWNLOADS=1
RUN make -j$(nproc) && make install

RUN useradd -r mysql && mkdir -p /usr/local/mysql/data && chown -R mysql:mysql /usr/local/mysql

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH="/usr/local/mysql/bin:$PATH"

WORKDIR /usr/local/mysql

EXPOSE 3306

ENTRYPOINT ["/entrypoint.sh"]
