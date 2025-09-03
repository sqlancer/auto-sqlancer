FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven git jq netcat mysql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/sqlancer

RUN git clone https://github.com/sqlancer/sqlancer.git . && \
    mvn clean package -DskipTests

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

CMD ["/root/entrypoint.sh"]

