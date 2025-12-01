# NER11 Sector Comparison: Energy vs. The Rest
**Date**: 2025-11-25
**Focus**: Comparative analysis of the Energy Sector (Custom + ElectricalNER) against the other 15 Critical Infrastructure Sectors.

---

## 1. Executive Summary
The **Energy Sector** is now the "Super-Sector" of the NER11 model.
*   **Energy Coverage**: ~12,105 Documents (Custom + ElectricalNER).
*   **Average Other Sector**: ~30 Documents (Custom Only).
*   **Imbalance**: Energy is **400x** more represented than any other sector.

## 2. Detailed Comparison Table

| Sector | Custom Docs | External Docs | Total Docs | Key Entities | Status |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Energy** | **105** | **12,000** | **12,105** | `IEC_61850`, `SUBSTATION`, `GRID` | **DOMINANT** |
| **Water** | 33 | 0 | 33 | `WATER_TREATMENT`, `PUMP` | **Weak** |
| **Transportation** | 80 | 0 | 80 | `RAIL_PROTOCOL`, `ADS-B` | **Moderate** |
| **Manufacturing** | 39 | 0 | 39 | `PLC`, `ROBOTICS` | **Weak** |
| **Chemical** | 30 | 0 | 30 | `HAZMAT`, `REACTOR` | **Weak** |
| **Financial** | 30 | 0 | 30 | `SWIFT`, `BANKING` | **Weak** |
| **Healthcare** | 29 | 0 | 29 | `PACS`, `HIPAA` | **Weak** |
| **IT/Telecom** | 42 | 0 | 42 | `5G`, `ROUTER` | **Moderate** |
| **Dams** | 51 | 0 | 51 | `HYDROELECTRIC` | **Moderate** |
| **Nuclear** | 4 | 0 | 4 | `RADIATION` | **Critical Gap** |
| **Defense** | 0 | 0 | 0 | - | **Missing** |
| **Food/Ag** | 0 | 0 | 0 | - | **Missing** |
| **Emergency** | 0 | 0 | 0 | - | **Missing** |
| **Government** | 0 | 0 | 0 | - | **Missing** |
| **Commercial** | 0 | 0 | 0 | - | **Missing** |
| **Communications** | 0 | 0 | 0 | - | **Missing** |

## 3. External Research Findings (Gap Analysis)
We conducted a comprehensive search for external datasets to fill these gaps.
**Result: No "Silver Bullet" Datasets Found.**

*   **Financial**: `FiNER-ORD` exists but focuses on financial reports/XBRL, not SWIFT transactions or cyber threats.
*   **Healthcare**: `i2b2` exists for de-identification, but no public dataset focuses on "HIPAA Cybersecurity" specifically.
*   **Telecom/5G**: `SPEC5G` exists for protocols, but no NER dataset for physical infrastructure components.
*   **Digital Twin**: No public NER datasets for "Digital Twin Ontology".
*   **Water/Rail/Mfg**: No public NER datasets found.

**Conclusion**:
The Custom Data is the **ONLY** source of truth for these specific domains. We cannot rely on external data to fix the imbalance.

## 4. Mitigation Strategy (Weighting)
To fix this, we must **Inverse Weight** the sectors during training.
*   **Energy Weight**: **0.5x** (Down-weight to prevent overfitting).
*   **Other Sectors Weight**: **5.0x** (Up-weight to force the model to pay attention to the scarce examples).

**Recommendation**:
We must treat the Energy Sector as a "General" dataset (like MITRE) and the other sectors as "Gold" (like Psychometrics).
