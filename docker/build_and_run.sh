#!/bin/bash

# Build and Run NER11 Docker Environment
echo "Building NER11 Docker Container..."
docker-compose build

echo "Starting Container..."
docker-compose up -d

echo "Container 'ner11_training_env' is running."
echo "To access the shell, run:"
echo "  docker exec -it ner11_training_env /bin/bash"
