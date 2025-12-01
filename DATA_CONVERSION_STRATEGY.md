# NER11 Data Conversion & Labeling Strategy

**Objective**: Ensure all Custom Data is accurately represented, weighted, and uniformly labeled consistent with the External Data and Master Schema.

## 1. Categorization & Weighting
We will classify the 1,600+ custom files into strict categories to ensure the model prioritizes high-value engineering data without discarding context.

| Category | Definition | Weight | Rationale |
| :--- | :--- | :--- | :--- |
| **A: Gold Standard** | Files ending in `_EXTRACT.md` in Sector folders. | **3.0x** | **Oversample**. These contain the specific engineering details (setpoints, protocols) we extracted. |
| **B: Standard Context** | All other text files (Standards, Wiki, Psychometrics, Lacan). | **1.0x** | **Baseline**. Provides broad context, definitions, and domain knowledge. **CRITICAL**: Includes all Psychometrics/Lacan. |
| **C: Reports** | `Annual_Cyber_Security_Reports/` | **0.0x** | **SKIP** (as requested). Will not be analyzed or trained on to reduce noise. |
| **D: Invalid** | Images, Binaries, Empty files. | **0.0x** | **Exclude**. Physically unusable. |

## 2. Label Uniformity Strategy
To ensure the **Custom Data** speaks the same language as the **External Data**:

1.  **Single Source of Truth**: The `NER11_ENTITY_MASTER_LIST.md` (568 types) is the absolute reference.
2.  **External Data**: Already harmonized to this list (e.g., `SQL_INJECTION` -> `CWE_WEAKNESS`).
3.  **Custom Data**: Will be **Auto-Labeled** using a strict `EntityRuler` derived from the Master List.
    *   *Example*: If a custom file says "The PLC-5 uses Modbus", the system will look up "PLC-5" and "Modbus" in the Master List and tag them `DEVICE` and `PROTOCOL`.

## 3. Label Coverage Verification (The "Deep Read")
Before converting, we must ensure our Master List actually covers the concepts in your Custom Data.

**Action: Deep Concept Discovery Scan**
I will run a script that reads **ALL** Category A and B files (skipping Reports) to:
1.  Extract high-frequency Noun Phrases and Keywords.
2.  Compare them against the current `NER11_ENTITY_MASTER_LIST`.
3.  **Identify Gaps**: Report terms that appear frequently but **DO NOT** have a corresponding label in our schema.
    *   *Example*: If "Ladder Logic" appears 500 times but isn't in our schema, I will flag it.

## 4. Execution Workflow
1.  **Run Deep Concept Discovery**: Generate `MISSING_CONCEPTS_REPORT.md`.
2.  **User Review**: You approve adding missing terms to the Master List.
3.  **Update Master List**: Add approved terms.
4.  **Execute Conversion**: Run `convert_custom_data.py` to generate `train.spacy` using the updated Master List and defined weights.

## 5. Approval Request
Do you approve this strategy?
1.  **Weights**: 3.0x (Gold), 1.0x (Standard), Skip Reports.
2.  **Gap Analysis**: Run the "Deep Concept Discovery" scan to find missing labels.
