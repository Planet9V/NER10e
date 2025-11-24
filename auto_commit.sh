#!/bin/bash
# Auto-commit script for NER10e

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Starting auto-commit for branch: $BRANCH at $TIMESTAMP"

# Add all changes
git add .

# Commit with timestamp
git commit -m "Auto-commit: Progress update at $TIMESTAMP"

# Push to remote
git push origin $BRANCH

echo "✅ Changes pushed to Planet9V/NER10e"
