# NER11 Gold Standard - Handover & Next Steps

**Date**: 2025-11-25
**Status**: Ready for Phase 4 (Merge & Train)

## 1. Current State Summary
We have successfully completed Phases 1-3 of the NER11 pipeline. The environment is primed for the final merge and training execution.

*   **Custom Data**: 1,600+ files converted to `.spacy`, auto-labeled with 580+ entities, and weighted (3.0x Gold / 1.0x Standard).
*   **External Data**: 9 datasets (500k+ docs) harmonized to the Master Schema.
*   **Infrastructure**: Docker environment (`docker/`) created with GPU support and 50GB RAM allocation.
*   **Strategy**: A "60k Target" merge strategy is defined to balance quality and quantity.

## 2. The "60k Strategy" (Critical Context)
We are **NOT** merging all 500k external documents. Doing so would drown out our high-value Custom Data (0.2%).
Instead, we are **Capping** the `CIRCL_vuln` dataset at 15,000 documents.

**Target Composition**:
*   **Custom Data**: ~1,300 docs (Weighted 3x)
*   **Threat Intel (MITRE/APT)**: ~22,000 docs
*   **Engineering (Electrical)**: ~15,000 docs
*   **Vulnerability (CIRCL)**: **CAPPED at 15,000 docs**
*   **Total**: ~61,300 Documents.

## 3. Immediate Next Steps (How to Proceed)

### Step A: Execute the Merge (One-Click)
The host (WSL) has limited RAM. **You must run the merge in Docker.**
I have created a helper script that handles building the container and running the merge script automatically.

```bash
cd /home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/docker
./run_merge.sh
```
*   **What this does**:
    1.  Checks if `ner11_training_env` container is running.
    2.  Builds/Starts it if needed (with GPU & 50GB RAM config).
    3.  Executes `python3 scripts/merge_datasets.py` *inside* the container.
*   **Output**: Creates `../final_training_set/train.spacy` and `dev.spacy`.

### Step B: Configure & Train
Once the merge is complete, you can enter the container to start training:
```bash
docker exec -it ner11_training_env /bin/bash
cd /app/NER11_Gold_Standard
# Run training command...
```

### Step C: Configure & Train
1.  Generate the config (using the `base_config.cfg` template, ensuring `gpu_allocator` is set).
2.  Run the training command:
```bash
python3 -m spacy train config.cfg --output ../models/ner11_v1 --paths.train ../final_training_set/train.spacy --paths.dev ../final_training_set/dev.spacy --gpu-id 0
```

## 4. Key Files for Reference
*   `DATASET_COMPARISON_REPORT.md`: Detailed rationale for the merge strategy.
*   `NER11_ENTITY_MASTER_LIST.md`: The official schema (580+ entities).
*   `scripts/merge_datasets.py`: The code logic for the merge.
