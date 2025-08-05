FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git build-essential libreadline-dev zlib1g-dev flex bison \
    libxml2-dev libxslt1-dev libssl-dev libicu-dev pkg-config \
    wget ca-certificates lsb-release pwgen && \
    apt-get clean

ENV PG_VERSION=17 \
    PG_USER=postgres \
    PG_BASE=/usr/local/pgsql \
    PG_DATADIR=/var/lib/postgresql/data

# Clone & build PostgreSQL from source
RUN git clone --depth 1 --branch REL_${PG_VERSION}_STABLE https://github.com/postgres/postgres.git /tmp/postgres && \
    cd /tmp/postgres && \
    ./configure --prefix=${PG_BASE} && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /tmp/postgres

# Create user and directories
RUN useradd -r -s /bin/bash ${PG_USER} && \
    mkdir -p ${PG_DATADIR} /var/run/postgresql && \
    chown -R ${PG_USER}:${PG_USER} ${PG_DATADIR} /var/run/postgresql ${PG_BASE}

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Update PATH
ENV PATH=${PG_BASE}/bin:$PATH

# Expose PostgreSQL port
EXPOSE 5432

# Run PostgreSQL with init and config
ENTRYPOINT ["/entrypoint.sh"]
