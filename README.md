# NER11 Gold Standard Model Repository

> [!IMPORTANT]
> **Repository Restoration Required**
> Due to GitHub file size limits, the `models` and `training_data` directories are stored as split archives.
> **Before using this repository, you MUST run the restoration script:**
> ```bash
> ./restore_repository.sh
> ```
> This will automatically recombine and extract all necessary files.

# NER11 Gold Standard Model Repository
oject State & Directory Structure
**Date**: 2025-11-25
**Status**: PHASE 3 COMPLETE - READY FOR TRAINING
**Location**: `/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/`

## 1. Project Overview
The `NER11_Gold_Standard` directory is the self-contained, portable home for the NER11 model training pipeline. It contains all necessary components: extracted intelligence (custom data), external community datasets, reference standards, Docker environment, and the final merged training set.

## 2. Current State Summary
**Status**: **Phase 3: Dataset Merge (COMPLETE) - Phase 4: Training (READY)**
*   **Phase 1**: Data Enhancement (Deep Research) - ✅ **COMPLETE**
*   **Phase 2**: External Data Acquisition & Harmonization - ✅ **COMPLETE**
*   **Phase 3**: Dataset Merge & Preparation - ✅ **COMPLETE**
*   **Phase 4**: Model Training - 🎯 **READY FOR EXECUTION**

### Merge Results (Completed 2025-11-25 20:21 CST)
- **Training Documents**: 67,230
- **Development Documents**: 9,037
- **Total Documents**: 76,267
- **Total Entities**: 306,053
- **Active Entity Types**: 61 (from 566 available)
- **Output Files**: `final_training_set/train.spacy` (44MB), `dev.spacy` (8.1MB)

> [!IMPORTANT]
> **NEXT STEP**: Training configuration and execution. See [TASKMASTER_TRAINING.md](TASKMASTER_TRAINING.md) for detailed instructions on configuring and running the model training with GPU acceleration.

## 3. Directory Structure & Contents

  - `Information_Technology/` (4 files)
  - `Nuclear/` (4 files)
  - `Public_Health/` (4 files)
  - `Transportation/` (4 files)
  - `Water/` (4 files)
- **Total Files**: 60+ Markdown files.

### 📂 `external_data/`
**Status**: Fully Populated & Portable
**Purpose**: Stores community datasets in both raw and converted formats.
- **`standardized/`**: Contains 9 subdirectories.
  - `01_APTNER/`: Full dataset (Train/Dev/Test + Raw .txt).
  - `02_CyNER/`: Full dataset (Train/Valid/Test + Raw).
  - `CIRCL_vuln/`: Full dataset (Train/Test JSONL + .spacy).
  - `CVE_NER/`: Full dataset (Train JSONL + .spacy).
  - `ElectricalNER/`: Full dataset (Train/Val/Test JSONL + .spacy).
  - `exploitdb/`: Full dataset (Raw CSV/files + .spacy).
  - `KEV_EPSS/`: Full dataset (Raw CSV + .spacy).
  - `MITRE_TTP/`: Full dataset (Train/Val/Test JSONL + .spacy).
  - `Open-CyKG/`: Full dataset (Raw + .spacy).
- **`EXTERNAL_DATASET_INVENTORY.md`**: Detailed inventory log.

### 📂 `reference/`
**Status**: Populated
**Purpose**: Reference schemas and standards.
- `NER11_ENTITY_SCHEMA.json` (Target Schema)
- `NER11_RELATIONSHIP_SCHEMA.json` (Target Schema)

### 📂 `scripts/`
**Status**: Pending Updates
**Purpose**: Python scripts for data conversion and training.
- *(Pending creation of custom data conversion script)*

### 📄 Root Files
- **`NER11_BLOTTER.md`**: The immutable audit log of all actions.
- **`TASKMASTER.md`**: The master runbook for the project.
- **`TASKMASTER_DATA_ENHANCEMENT.md`**: The specific runbook for Phase 1.
- **`README.md`**: This file.

## 4. Next Steps
1.  **Generate Training Configuration**: Create `env/config.cfg` optimized for transformer-based NER with GPU support.
2.  **Execute Model Training**: Train NER11 model on 76,267 documents using CUDA acceleration.
3.  **Evaluate Model Performance**: Calculate F1 scores, precision, recall per entity type.
4.  **Deploy Model**: Package and integrate with AEON Cyber Digital Twin.

## 5. Final Training Set Location
- **Path**: `final_training_set/`
- **Files**: `train.spacy` (67,230 docs), `dev.spacy` (9,037 docs)
- **Status**: ✅ Ready for training

## 6. Docker Environment
- **Container**: `ner11_training_env` (RUNNING)
- **Image**: `ner11-gold-standard:latest` (29.3GB)
- **GPU**: NVIDIA GeForce RTX 4060 (8GB VRAM)
- **Memory**: 16GB shared memory allocated
- **Access**: `docker exec -it ner11_training_env /bin/bash`

## 7. Directory Structure (Updated)### `docker/`
*   **`Dockerfile`**: NVIDIA CUDA-based image with spaCy, Transformers, and GPU support.
*   **`docker-compose.yml`**: Configuration for 50GB RAM allocation and GPU passthrough.
*   **`build_and_run.sh`**: Helper script to launch the environment.
*   **`run_merge.sh`**: **One-Click Script** to build container and run the dataset merge.

## 5. Data Categorization & Weighting Strategy
To ensure the model prioritizes engineering-grade data, we will apply the following weighting strategy during standardization:

| Category | Description | Weight | Action |
| :--- | :--- | :--- | :--- |
| **A: Gold Standard** | High-density engineering extracts (e.g., `_EXTRACT.md`). | **3.0x** | Oversample. |
| **B: Technical Ref** | Standards, frameworks, **Psychometrics, Lacan**. | **1.0x** | Standard. |
| **C: General Reports** | High-level summaries (e.g., `Annual_Reports`). | **0.2x** | Downsample. |
## 8. Hardware Constraints & Optimization Strategies

### 8.1. Local Training (8GB VRAM Constraint)
**Current Configuration**: Optimized for NVIDIA RTX 4060 (8GB).
*   **Window Size**: `64` (Reduced from 512).
    *   *Impact*: Limits context awareness to ~64 tokens. Max theoretical F1 ~90%.
*   **Batch Size**: `8` (Physical) with `accumulate_gradient = 8` (Effective Batch = 64).
*   **Data Slicing**: Strict filtering of "Monster Tokens" (>100 chars) to prevent OOM crashes.
*   **Warning**: `Token indices sequence length is longer than the specified maximum...` is expected and handled via safe truncation.

### 8.2. High-Performance Training (AWS / Cloud)
**Target Hardware**: NVIDIA A10G (24GB) or A100 (40GB+).
**Recommended Configuration**:
*   **Window Size**: `128` or `256` (Restores full context).
    *   *Impact*: Enables detection of long-range dependencies. Max F1 >94%.
*   **Batch Size**: `32` (Physical).
*   **Accumulate Gradient**: `4`.
*   **Model**: Upgrade from `roberta-base` to `roberta-large` for maximum accuracy.

### 8.3. Migration Strategy
To migrate to AWS:
1.  Deploy the `NER11_AEON_Gold_2_Portable` package.
2.  Update `env/config.cfg`: Set `window = 128` and `batch_size = 32`.
3.  Re-run `scripts/slice_and_stride_data.py` with `WINDOW_SIZE = 128`.
4.  Execute training.
