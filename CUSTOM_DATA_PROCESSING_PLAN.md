# NER11 Custom Data Processing Plan

**Date**: 2025-11-25
**Status**: DRAFT FOR APPROVAL
**Objective**: Prepare `custom_data/source_files` for training by categorizing, weighting, and converting files.

## 1. Categorization Strategy
We will classify all 2,600+ files into 4 categories based on "Entity Density" and "Relevance".

### **Category A: Gold Standard (High Value)**
*   **Description**: Engineering-grade extracts created during Phase 1. High density of specific entities (protocols, setpoints, standards).
*   **Location**: The 60+ files recently moved to sector folders (e.g., `Chemical_Sector/OSHA_PSM_...`).
*   **Training Weight**: **3.0x** (Oversample to ensure model learns these specifics).
*   **Action**: Convert to `.spacy` with strict span filtering.

### **Category B: Technical Reference & Psychometrics (Medium Value)**
*   **Description**: Standards, frameworks, technical guides, **Psychometrics, Psychoanalysis (Lacan), and Cognitive Bias** data.
*   **Examples**: `IEC_62443/`, `MITRE_Framework/`, `Ontologies/`, `Wiki_Agent_Red/` (Lacan, Behavioral profiles), `Psychometrics/`.
*   **Training Weight**: **1.0x** (Standard weight - **CRITICAL: DO NOT DISCOUNT**).
*   **Action**: Convert to `.spacy`.

### **Category C: General Reports (Low Value)**
*   **Description**: High-level summaries, annual reports, news. Good for general vocabulary but low entity density.
*   **Examples**: `Annual_Cyber_Security_Reports/` (e.g., "October 2025 Threat Landscape").
*   **Training Weight**: **0.2x** (Downsample to prevent washing out technical terms).
*   **Action**: Convert but heavily sample or cap the number of documents.

### **Category D: Noise / Irrelevant (Exclude)**
*   **Description**: Files that are not useful for NER training.
*   **Examples**:
    *   `Zone.Identifier` files (metadata junk).
    *   `.png`, `.jpg` images (cannot be trained on).
    *   Empty files or files < 1KB (unless specific lists).
*   **Action**: **SKIP** during conversion.

## 2. Processing Plan

### Step 1: Scan & Map
*   Run a script to scan all 2,600 files.
*   Generate a `manifest.json` mapping each file to a Category (A, B, C, D).
*   **Heuristic**:
    *   If filename contains `_EXTRACT.md` AND is in a Sector folder -> **Cat A**.
    *   If folder is `Psychometrics`, `Cognitive_Biases`, `Personality_Frameworks` -> **Cat B**.
    *   If content contains "Lacan" or "Psychoanalysis" -> **Cat B**.
    *   If folder is `Annual_Cyber_Security_Reports` -> **Cat C**.
    *   If file extension is not `.md`, `.txt`, `.json`, `.csv` -> **Cat D**.

### Step 2: User Review
*   Present the `manifest.json` summary to User.
*   "Found 64 Gold files, 1500 Technical files, 800 Reports, 200 Junk files."
*   Ask for approval to proceed.

### Step 3: Conversion
*   Execute `convert_custom_data.py`.
*   This script will read the manifest and apply the weights during the `.spacy` creation process (using `corpus.weight` or by duplicating examples).

## 3. Immediate Action Required
*   **Approve this plan** to proceed with the Scan & Map phase.
