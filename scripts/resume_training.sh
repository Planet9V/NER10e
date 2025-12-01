#!/bin/bash
set -e

# Define paths (inside container)
MODEL_DIR="/app/NER11_Gold_Standard/models/ner11_v1"
BACKUP_DIR="/app/NER11_Gold_Standard/models/ner11_v1_backup"
LOG_FILE="/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/resume_training.log"

echo "Starting resumption process..." | tee -a "$LOG_FILE"

# Backup existing model (using docker to avoid permission issues)
echo "Backing up existing model to $BACKUP_DIR (inside container)..." | tee -a "$LOG_FILE"
docker exec ner11_training_env bash -c "if [ -d '$BACKUP_DIR' ]; then rm -rf '$BACKUP_DIR'; fi; cp -r '$MODEL_DIR' '$BACKUP_DIR'"
echo "Backup complete." | tee -a "$LOG_FILE"

# Execute training inside docker
echo "Executing training command..." | tee -a "$LOG_FILE"
docker exec ner11_training_env python3 -m spacy train \
  /app/NER11_Gold_Standard/env/config_resume.cfg \
  --output /app/NER11_Gold_Standard/models/ner11_v1_resumed \
  --paths.train /app/NER11_Gold_Standard/final_training_set/train.spacy \
  --paths.dev /app/NER11_Gold_Standard/final_training_set/dev.spacy \
  --gpu-id 0 >> "$LOG_FILE" 2>&1

echo "Training command finished. Check $LOG_FILE for details." | tee -a "$LOG_FILE"
