#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting NER11 Training Setup (Local Gold Standard)...${NC}"

# Ensure we are in the right directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo -e "${GREEN}Building and Starting Docker Container...${NC}"
# Build and start the container in detached mode
docker compose -f docker/docker-compose.yml up -d --build

echo -e "${GREEN}Waiting for container to initialize...${NC}"
sleep 10

echo -e "${GREEN}Starting Training...${NC}"
# Execute the training command inside the container
# Note: The docker-compose mounts the current directory to /app/NER11_Gold_Standard
docker exec ner11_training_env python3 -m spacy train \
    /app/NER11_Gold_Standard/env/config.cfg \
    --output /app/NER11_Gold_Standard/models/ner11_v3 \
    --paths.train /app/NER11_Gold_Standard/final_training_set/train_sliced.spacy \
    --paths.dev /app/NER11_Gold_Standard/final_training_set/dev_sliced.spacy \
    --gpu-id 0

echo -e "${GREEN}Training Complete!${NC}"
