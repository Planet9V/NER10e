#!/bin/bash
set -e

# Define paths (inside container)
CONFIG_FILE="/app/NER11_Gold_Standard/env/config.cfg"
OUTPUT_DIR="/app/NER11_Gold_Standard/models/ner11_v2"
TRAIN_PATH="/app/NER11_Gold_Standard/final_training_set/train.spacy"
DEV_PATH="/app/NER11_Gold_Standard/final_training_set/dev.spacy"
LOG_FILE="/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/training_v2.log"

echo "Starting fresh training run (v2)..." | tee -a "$LOG_FILE"

# Execute training inside docker
echo "Executing training command..." | tee -a "$LOG_FILE"
docker exec ner11_training_env python3 -m spacy train \
  "$CONFIG_FILE" \
  --output "$OUTPUT_DIR" \
  --paths.train "$TRAIN_PATH" \
  --paths.dev "$DEV_PATH" \
  --gpu-id 0 >> "$LOG_FILE" 2>&1

echo "Training command finished. Check $LOG_FILE for details." | tee -a "$LOG_FILE"
