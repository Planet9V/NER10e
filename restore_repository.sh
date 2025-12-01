#!/bin/bash
# restore_repository.sh
# NER11 Gold Standard - Automated Restoration Script
# 
# This script automatically recombines the split archive files for the models
# and training data, then extracts them to their original locations.
#
# Usage: ./restore_repository.sh

set -e

echo "========================================================"
echo "   NER11 Gold Standard - Repository Restoration Tool    "
echo "========================================================"

# Function to restore a split archive
restore_archive() {
    local name=$1
    local part_prefix=$2
    
    echo ""
    echo "Checking for $name archives..."
    
    if ls ${part_prefix}* 1> /dev/null 2>&1; then
        echo "-> Found split parts for $name. Recombining..."
        cat ${part_prefix}* > ${name}.tar.gz
        
        echo "-> Extracting $name..."
        tar -xzf ${name}.tar.gz
        
        echo "-> Cleaning up temporary tarball..."
        rm ${name}.tar.gz
        
        echo "-> $name successfully restored!"
    else
        echo "-> No split archives found for $name. Skipping."
    fi
}

# 1. Restore Models
restore_archive "models" "models.tar.gz.part_"

# 2. Restore Training Data
restore_archive "training_data" "training_data.tar.gz.part_"

echo ""
echo "========================================================"
echo "   Restoration Complete!                                "
echo "========================================================"
echo "You can now run the training or inference scripts."
