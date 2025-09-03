FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven git jq netcat mysql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/sqlancer

ARG DUCKDB_JDBC_VERSION=1.2.2.0 

RUN git clone https://github.com/sqlancer/sqlancer.git . && \
    mvn -q versions:use-dep-version \
        -Dincludes=org.duckdb:duckdb_jdbc \
        -DdepVersion=${DUCKDB_JDBC_VERSION} \
        -DforceVersion=true && \
    mvn -q clean package -DskipTests

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
CMD ["/root/entrypoint.sh"]
