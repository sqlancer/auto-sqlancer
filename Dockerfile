# 使用官方 MySQL 8 镜像作为基础
FROM mysql:8.0


# 健康检查
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
  CMD mysqladmin ping -h 127.0.0.1 -u root -p$MYSQL_ROOT_PASSWORD || exit 1
