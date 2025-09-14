FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven git jq netcat sqlite3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/sqlancer

ARG SQLITE_JDBC_VERSION=3.45.1.0

RUN git clone https://github.com/sqlancer/sqlancer.git . && \
    mvn -q versions:use-dep-version \
        -Dincludes=org.xerial:sqlite-jdbc \
        -DdepVersion=${SQLITE_JDBC_VERSION} \
        -DforceVersion=true && \
    mvn -q clean package -DskipTests

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

CMD ["/root/entrypoint.sh"]
