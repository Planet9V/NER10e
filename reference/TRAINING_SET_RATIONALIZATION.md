# NER11 Rationalized Training Set Evaluation
**Date**: 2025-11-25
**Objective**: Optimize the training set by leveraging overlap between Custom Data and External Datasets.

This document evaluates the synergy between the user's custom corpus and the acquired community datasets to define the **Optimum Training Set**.

---

## 1. The "Psychometric" Layer (Unique Value)
*   **Custom Data**: 585 files (Biases, Personality, Red Team).
*   **External Data**: *None*.
*   **Synergy**: **Zero Overlap**. This is the unique differentiator of the NER11 model.
*   **Optimization**: Must be weighted heavily (**5.0x**) to ensure the model learns these rare entities (`COGNITIVE_BIAS`, `LACANIAN_DISCOURSE`) which are absent in general corpora.

## 2. The "Threat Intel" Layer (High Synergy)
*   **Custom Data**: 290 files (MITRE, IOCs, CVEs).
*   **External Data**:
    *   `MITRE_TTP` (3.5k docs): Comprehensive TTP coverage.
    *   `ExploitDB` (45k docs): Massive exploit database.
    *   `KEV_EPSS` (Known Exploited Vulns).
    *   `APTNER` (10k docs): APT reports.
*   **Synergy**: **High Overlap**. The custom data provides high-quality, curated examples, while the external data provides volume.
*   **Optimization**:
    *   Use Custom Data as "Gold Standard" (Weight **2.0x**).
    *   Use External Data for volume (Weight **1.0x**).
    *   *Result*: The model learns the general patterns from External, but fine-tunes on the specific phrasing in Custom.

## 3. The "Infrastructure" Layer (Contextual Synergy)
*   **Custom Data**: 443 files (Energy, Water, Rail).
*   **External Data**:
    *   `ElectricalNER` (12k docs): Power grid specifics.
    *   `ICS-Flow` (Network traffic - *Excluded for now*).
*   **Synergy**: **Medium Overlap**. `ElectricalNER` covers the Energy sector well, but Custom Data covers Water, Rail, and Manufacturing which are missing externally.
*   **Optimization**:
    *   Custom Data (Weight **3.0x**) is critical for non-Energy sectors.
    *   `ElectricalNER` (Weight **1.0x**) reinforces the Energy domain.

## 4. The "Safety" Layer (Critical Gap Fill)
*   **Custom Data**: 117 files (HAZOP, FMEA, IEC 62443).
*   **External Data**: *None*.
*   **Synergy**: **Zero Overlap**. Similar to Psychometrics, this is a unique domain.
*   **Optimization**: Must be weighted heavily (**4.0x**) to ensure Safety entities (`HAZARD`, `SIL`) are not drowned out by the massive volume of generic cyber terms.

---

## 5. The Optimum Training Set (Rationalized)

Based on this evaluation, the **NER11 Gold Image** should be constructed as follows:

| Component | Source | Docs | Weight | Role |
| :--- | :--- | :---: | :---: | :--- |
| **Core Identity** | **Custom Psychometrics** | 585 | **5.0x** | Defines the "Human" insight. |
| **Safety Critical** | **Custom RAMS/Safety** | 117 | **4.0x** | Defines the "Physical" consequence. |
| **Context Anchor** | **Custom Infrastructure** | 443 | **3.0x** | Broadens sector coverage. |
| **Threat Volume** | **External (MITRE, ExploitDB)** | ~50k | **1.0x** | Provides massive variation for TTPs/CVEs. |
| **Energy Boost** | **External (ElectricalNER)** | 12k | **1.0x** | Deepens Energy sector knowledge. |
| **General Cyber** | **External (APTNER, CyNER)** | ~15k | **0.5x** | Background noise/general competence. |

**Total Estimated Size**: ~80,000 Documents
**RAM Requirement**: ~40-50GB (Perfect for "Titan" configuration).
