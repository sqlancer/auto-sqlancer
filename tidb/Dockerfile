
    FROM golang:1.23 AS builder

    ARG TIDB_VERSION=master
    ENV TIDB_VERSION=${TIDB_VERSION}
    
    WORKDIR /go/src/github.com/pingcap
    

    RUN git clone --depth=1 --branch=${TIDB_VERSION} https://github.com/pingcap/tidb.git
    
    WORKDIR /go/src/github.com/pingcap/tidb
    

    RUN make 
    

    FROM debian:bookworm-slim

    WORKDIR /tidb
    COPY --from=builder /go/src/github.com/pingcap/tidb/bin/tidb-server .

    EXPOSE 4000
    ENTRYPOINT ["./tidb-server"]
    