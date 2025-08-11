# FROM ubuntu:20.04

# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && \
#     apt-get install -y openjdk-17-jdk maven git jq netcat mysql-client && \
#     rm -rf /var/lib/apt/lists/*

# WORKDIR /root/sqlancer

# RUN git clone https://github.com/sqlancer/sqlancer.git . && \
#     mvn clean package -DskipTests

# COPY entrypoint.sh /root/entrypoint.sh
# RUN chmod +x /root/entrypoint.sh

# CMD ["/root/entrypoint.sh"]

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      openjdk-17-jdk maven git jq netcat mysql-client \
      curl ca-certificates bash grep sed && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/sqlancer

ARG SQLANCER_REF=main

RUN git clone https://github.com/sqlancer/sqlancer.git . && \
    git checkout "${SQLANCER_REF}" && \
    echo ">>> scanning for deprecated CockroachDB settings..." && \
    PC_ENABLED_FILES="$(grep -RIl 'sql.metrics.statement_details.plan_collection.enabled' || true)" && \
    if [ -n "$PC_ENABLED_FILES" ]; then \
      echo "$PC_ENABLED_FILES" | xargs -r sed -i "/sql.metrics.statement_details.plan_collection.enabled/d"; \
    fi && \
    PC_PERIOD_FILES="$(grep -RIl 'sql.metrics.statement_details.plan_collection.period' || true)" && \
    if [ -n "$PC_PERIOD_FILES" ]; then \
      echo "$PC_PERIOD_FILES" | xargs -r sed -i "/sql.metrics.statement_details.plan_collection.period/d"; \
    fi && \
    mvn -q -DskipTests clean package

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

CMD ["/root/entrypoint.sh"]


