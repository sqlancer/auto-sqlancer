#!/bin/bash
set -e

CONFIG_JSON="config.json"

# Default parameters
MODE="test"
DOCKER_IMAGE_NAME=""
DBMS=""
VERSION=""
THREADS=""
TIMEOUT=""
ORACLE=""
SQL_PASSWORD=""

# Parse command-line arguments
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
      MODE="test_single"
      DBMS="$2"
      VERSION="$3"
      shift 3
      ;;
    --test)
      if [[ "$2" == "all" ]]; then
        MODE="test_all"
        shift 2
      else
        echo "Unknown argument: $1 $2"
        exit 1
      fi
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
      echo "Usage:"
      echo "  Build base image: ./test.sh --docker -name [image_name]"
      echo "  Build + pull DBMS image: ./test.sh --docker -name [image_name] -db [dbms] [version]"
      echo "  Run test: ./test.sh --test-db [dbms] [version] --num-threads [n] --timeout-seconds [s] --oracle [o] --password [p]"
      echo "  Test all DBMSs: ./test.sh --test all --num-threads [n] --timeout-seconds [s] --oracle [o] --password [p]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Load defaults from config.json
THREADS=${THREADS:-$(jq -r '.num_threads' $CONFIG_JSON)}
TIMEOUT=${TIMEOUT:-$(jq -r '.timeout_seconds' $CONFIG_JSON)}
ORACLE=${ORACLE:-$(jq -r '.oracle' $CONFIG_JSON)}
SQL_PASSWORD=${SQL_PASSWORD:-$(jq -r '.password' $CONFIG_JSON)}

# === Build docker image ===
if [[ "$MODE" == "docker" ]]; then
  if [[ -z "$DOCKER_IMAGE_NAME" ]]; then
    echo "❌ Please specify image name with -name"
    exit 1
  fi

  echo "=== [STEP] Generating Dockerfile ==="
  if [[ -n "$DBMS" && -n "$VERSION" ]]; then
    python3 generate_dockerfile.py "$DBMS" "$VERSION"
  else
    python3 generate_dockerfile.py
  fi

  echo "=== [STEP] Building image $DOCKER_IMAGE_NAME ==="
  sudo docker build -t "$DOCKER_IMAGE_NAME" .

  if [[ -n "$DBMS" && -n "$VERSION" ]]; then
    echo "=== [STEP] Pulling DBMS image: $DBMS:$VERSION ==="
    python3 -c "import ${DBMS}.docker_ops as db; db.pull_docker_image('${VERSION}')"
  fi

  echo "✅ Image build complete: $DOCKER_IMAGE_NAME"
  exit 0
fi

# === Run a single DBMS test ===
run_test() {
  local dbms="$1"
  local version="$2"
  local threads="$3"
  local timeout="$4"
  local oracle="$5"
  local password="$6"

  if [[ "$dbms" == "postgres" ]]; then
    SQL_USERNAME="postgres"
  elif [[ "$dbms" == "mysql" ]]; then
    SQL_USERNAME="root"
  else
    echo "❌ Unsupported DBMS: $dbms"
    exit 1
  fi

  IMAGE_NAME="sqlancer-auto-${dbms,,}-${version//./-}"

  echo "=== [INFO] Test Configuration ==="
  echo "DBMS: $dbms | Version: $version"
  echo "Threads: $threads | Timeout: $timeout | Oracle: $oracle"
  echo "User: $SQL_USERNAME"

  python3 generate_dockerfile.py "$dbms" "$version"
  sudo docker build -t "$IMAGE_NAME" .

  sudo docker run --rm \
    -e DBMS="$dbms" \
    -e VERSION="$version" \
    -e SQLANCER_THREADS="$threads" \
    -e SQLANCER_TIMEOUT="$timeout" \
    -e SQLANCER_ORACLE="$oracle" \
    -e SQLANCER_USERNAME="$SQL_USERNAME" \
    -e SQLANCER_PASSWORD="$password" \
    "$IMAGE_NAME"
}

# === Single DBMS test ===
if [[ "$MODE" == "test_single" ]]; then
  run_test "$DBMS" "$VERSION" "$THREADS" "$TIMEOUT" "$ORACLE" "$SQL_PASSWORD"
  exit 0
fi

# === All DBMS test ===
if [[ "$MODE" == "test_all" ]]; then
  for dir in */; do
    dbms=${dir%/}
    if [[ -f "$dbms/docker_ops.py" ]]; then
      version=$(jq -r --arg d "$dbms" '.versions[$d]' "$CONFIG_JSON")
      run_test "$dbms" "$version" "$THREADS" "$TIMEOUT" "$ORACLE" "$SQL_PASSWORD"
    fi
  done
  exit 0
fi
