#!/bin/bash
set -e

CONFIG_JSON="config.json"

# Default Configuration
MODE="test"
DOCKER_IMAGE_NAME=""
DBMS=""
VERSION=""
THREADS=""
TIMEOUT=""
ORACLE=""
SQL_PASSWORD=""

# Parse parameters
while [[ $# -gt 0 ]]; do
  case "$1" in
    --docker)
      MODE="docker"
      shift
      ;;
    -name)
      DOCKER_IMAGE_NAME="$2"
      shift 2
      ;;
    -db)
      DBMS="$2"
      VERSION="$3"
      shift 3
      ;;
    --test-db)
      DBMS="$2"
      VERSION="$3"
      shift 3
      ;;
    --num-threads)
      THREADS="$2"
      shift 2
      ;;
    --timeout-seconds)
      TIMEOUT="$2"
      shift 2
      ;;
    --oracle)
      ORACLE="$2"
      shift 2
      ;;
    --password)
      SQL_PASSWORD="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage"
      echo "  Build basic docker: ./test.sh --docker -name [docker_name]"
      echo "  Build + pull database：./test.sh --docker -name [docker_name] -db [dbms] [version]"
      echo "  Run test./test.sh --test-db [dbms] [version] --num-threads [n] --timeout-seconds [s] --oracle [o] --password [p]"
      exit 0
      ;;
    *)
      echo "Unknown parameters: $1"
      exit 1
      ;;
  esac
done

# === Build docker ===
if [[ "$MODE" == "docker" ]]; then
  if [[ -z "$DOCKER_IMAGE_NAME" ]]; then
    echo "❌ Use -name to identify docker's name"
    exit 1
  fi

  echo "=== [STEP] Generate Dockerfile ==="
  if [[ -n "$DBMS" && -n "$VERSION" ]]; then
    python3 generate_dockerfile.py "$DBMS" "$VERSION"
  else
    python3 generate_dockerfile.py
  fi

  echo "=== [STEP] Build docker $DOCKER_IMAGE_NAME ==="
  sudo docker build -t "$DOCKER_IMAGE_NAME" .

  if [[ -n "$DBMS" && -n "$VERSION" ]]; then
    echo "=== [STEP] pull DBMS: $DBMS:$VERSION ==="
    python3 -c "import ${DBMS}.docker_ops as db; db.pull_docker_image('${VERSION}')"
  fi

  echo "✅ Docker built: $DOCKER_IMAGE_NAME"
  exit 0
fi

# === Test ===
DBMS=${DBMS:-$(jq -r '.dbms' $CONFIG_JSON)}
VERSION=${VERSION:-$(jq -r '.version' $CONFIG_JSON)}
THREADS=${THREADS:-$(jq -r '.num_threads' $CONFIG_JSON)}
TIMEOUT=${TIMEOUT:-$(jq -r '.timeout_seconds' $CONFIG_JSON)}
ORACLE=${ORACLE:-$(jq -r '.oracle' $CONFIG_JSON)}
SQL_PASSWORD=${SQL_PASSWORD:-$(jq -r '.password' $CONFIG_JSON)}
SQL_USERNAME=$(jq -r --arg db "$DBMS" '.db_user_map[$db]' "$CONFIG_JSON")


IMAGE_NAME="sqlancer-auto-${DBMS,,}-${VERSION//./-}"

echo "=== [INFO] Test Configuration ==="
echo "DBMS: $DBMS | Version: $VERSION"
echo "Threads: $THREADS | Timeout: $TIMEOUT | Oracle: $ORACLE"
echo "User: $SQL_USERNAME"

# Generate Dockerfile
python3 generate_dockerfile.py "$DBMS" "$VERSION"

# Build docker
sudo docker build -t "$IMAGE_NAME" .

# Run docker and pass in parameters
sudo docker run --rm \
  -e DBMS="$DBMS" \
  -e VERSION="$VERSION" \
  -e SQLANCER_THREADS="$THREADS" \
  -e SQLANCER_TIMEOUT="$TIMEOUT" \
  -e SQLANCER_ORACLE="$ORACLE" \
  -e SQLANCER_USERNAME="$SQL_USERNAME" \
  -e SQLANCER_PASSWORD="$SQL_PASSWORD" \
  "$IMAGE_NAME"


