# NER11 TASKMASTER CONTROL CENTER
**Mission**: Operationalize NER11 Gold Standard Model for AEON Cyber Digital Twin
**Date**: 2025-11-25
**Version**: 1.0
**Status**: ACTIVE

---

## 1. Operational Architecture
This project follows a strict **Traceable, Repeatable, Reliable, Auditable** workflow. All actions are logged in `NER11_BLOTTER.md`.

### Roles & Responsibilities
*   **ARCHITECT**: Schema definition, Ontology alignment.
*   **DATA_OPS**: Data ingestion, cleaning, standardization.
*   **ML_ENGINEER**: Model configuration, training, evaluation.
*   **QA_OFFICER**: Verification, Unit Testing, Quality Gates.

---

## 2. Reference Documentation (APA Style)
All tasks are grounded in the following authoritative documents:

1.  **Entity Master List**: *NER11 Gold Standard - Entity Master List (Version 1.0)*. (2025). Located at `reference/NER11_ENTITY_MASTER_LIST.md`. Defines the 566 entity types used in this model.
2.  **Executive Definitions**: *NER11 Entity Definitions - Executive Summary*. (2025). Located at `reference/ENTITY_DEFINITIONS_EXECUTIVE.md`. Explains the strategic value of each entity category.
3.  **Custom Data Catalog**: *NER11 Custom Data Catalog*. (2025). Located at `custom_data/CUSTOM_DATA_CATALOG.md`. Inventories the 1,600+ custom files and defines the weighting strategy.

---

## 3. Master Workflow (The Plan)

### Phase 1: Foundation (Current)
*   [x] **Task 1.1**: Initialize Directory Structure & Blotter (`ARCHITECT`)
    *   *Deliverable*: `NER11_Gold_Standard/` directory, `NER11_BLOTTER.md`.
*   [x] **Task 1.2**: Populate Reference Documentation (`ARCHITECT`)
    *   *Deliverable*: `reference/NER11_ENTITY_MASTER_LIST.md`, `reference/ENTITY_DEFINITIONS_EXECUTIVE.md`.
*   [x] **Task 1.3**: Populate Custom Data (`DATA_OPS`)
    *   *Deliverable*: `custom_data/CUSTOM_DATA_CATALOG.md`, `custom_data/source_files/`.
*   [ ] **Task 1.4**: Create Taskmaster & Governance (`ARCHITECT`) **<-- CURRENT**
    *   *Deliverable*: `TASKMASTER.md` (this file).

### Phase 2: Data Acquisition & Standardization
*   [ ] **Task 2.1**: Download External Datasets (`DATA_OPS`)
    *   *Objective*: Acquire MITRE, ExploitDB, KEV, etc.
    *   *Reference*: `external_data/EXTERNAL_DATASET_INVENTORY.md` (To be created).
*   [ ] **Task 2.2**: Standardize External Data (`DATA_OPS`)
    *   *Objective*: Convert all external datasets to `.spacy` format using the Official Schema.
    *   *Output*: `external_data/standardized/*.spacy`.
*   [ ] **Task 2.3**: Standardize Custom Data (`DATA_OPS`)
    *   *Objective*: Convert `custom_data/source_files/` to `.spacy` format using the Official Schema.
    *   *Output*: `custom_data/standardized/custom.spacy`.

### Phase 3: Configuration & Training
*   [ ] **Task 3.1**: Generate Configuration (`ML_ENGINEER`)
    *   *Objective*: Create `env/config_ner11.cfg` optimized for 50GB RAM (Transformer).
*   [ ] **Task 3.2**: Create Training Script (`ML_ENGINEER`)
    *   *Objective*: Create `scripts/train_ner11_titan.sh`.
*   [ ] **Task 3.3**: Execute Training (`ML_ENGINEER`)
    *   *Objective*: Run the training pipeline.

### Phase 4: Validation & Deployment
*   [ ] **Task 4.1**: Evaluate Model (`QA_OFFICER`)
    *   *Objective*: Calculate F1 scores per category.
*   [ ] **Task 4.2**: Package for Deployment (`DATA_OPS`)
    *   *Objective*: Create Dockerfile and HuggingFace upload script.

---

## 4. Quality Gates
1.  **Ingestion Gate**: All entities must map to `NER11_ENTITY_MASTER_LIST.md`.
2.  **Training Gate**: No OOM errors. Loss must converge.
3.  **Validation Gate**: Psychometric F1 > 0.80. Technical F1 > 0.85.
