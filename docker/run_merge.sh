#!/bin/bash

# run_merge.sh
# Executes the dataset merge script INSIDE the Docker container.
# This ensures consistent environment and memory handling.

# 1. Ensure Container is Running
echo "[Docker] Checking container status..."
if [ ! "$(docker ps -q -f name=ner11_training_env)" ]; then
    if [ "$(docker ps -aq -f name=ner11_training_env)" ]; then
        echo "[Docker] Starting existing container..."
        docker start ner11_training_env
    else
        echo "[Docker] Building and starting new container..."
        docker-compose up -d --build
    fi
fi

# 2. Execute Merge Script
echo "[Docker] Executing merge_datasets.py inside container..."
docker exec ner11_training_env python3 /app/NER11_Gold_Standard/scripts/merge_datasets.py

echo "[Docker] Merge Complete. Check final_training_set/ for results."
