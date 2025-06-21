#!/bin/bash
set -e

# 1. Generate Dockerfile
echo "[STEP 1] Generating Dockerfile from config.json..."
python3 generate_dockerfile.py

# 2. Build docker
echo "[STEP 2] Building Docker image 'sqlancer-auto'..."
sudo docker build -t sqlancer-auto .

# 3. Run test
echo "[STEP 3] Running SQLancer test container..."
sudo docker run --rm sqlancer-auto

echo "[✔] All steps completed successfully!"
