# Dataset Comparison & Merge Impact Report

**Objective**: Analyze the composition of the **Custom Data** (Internal) vs. **External Data** (Community) to determine the best merging and weighting strategy.

## 1. Dataset Composition Comparison

| Feature | **Custom Data (Internal)** | **External Data (Community)** |
| :--- | :--- | :--- |
| **Source** | Deep Research Extracts, Standards, Wiki | MITRE, ExploitDB, CISA KEV, ElectricalNER |
| **Volume** | ~1,300 Documents | ~500,000+ Documents (Sampled) |
| **Focus** | **Engineering Depth**, Protocols, Specs | **Breadth**, Vulnerabilities, Threat Intel |
| **Key Labels** | `FREQUENCY`, `UNIT_OF_MEASURE`, `HARDWARE_COMPONENT`, `OPERATION_MODE` | `MEASUREMENT`, `DEVICE`, `CVE`, `CWE_WEAKNESS`, `MALWARE` |
| **Strengths** | High specificity, context-rich, "Gold Standard" accuracy. | Massive scale, diverse examples, standard threat coverage. |
| **Weaknesses** | Smaller volume. | Noisier, less specific to *our* sectors (e.g., Water/Energy specifics). |

## 2. Label Overlap & Gaps

| Category | Custom Data Status | External Data Status | **Merge Impact** |
| :--- | :--- | :--- | :--- |
| **Engineering** | **Strong**: `PSI`, `MW`, `MHz` (New Tiers) | **Moderate**: `MEASUREMENT` (14k), `DEVICE` (11k) | **High Synergy**. Custom data adds *precision* to External's *volume*. |
| **Vulnerability** | **Contextual**: Mentions in reports. | **Dominant**: `CVE` (6k), `CWE_WEAKNESS` (5k) | External data provides the bulk of vulnerability training. |
| **Threat Intel** | **Specific**: `Volt Typhoon`, `APT28`. | **Broad**: `APT_GROUP` (4k), `MALWARE` (5k). | Custom data anchors the model on *priority* threats. |
| **Operations** | **Strong**: `Manual`, `Auto`, `Redundant`. | **Weak**: Few operational state labels. | **Critical Add**. Custom data fills a major gap in External data. |

## 3. Weighting Strategy & Impact

To ensure the **Custom Data** (our "Gold" intelligence) isn't drowned out by the massive External datasets, we must apply aggressive weighting.

| Dataset Type | Proposed Weight | Impact on Model |
| :--- | :--- | :--- |
| **Custom (Gold)** | **3.0x** | Model will strongly prefer our specific engineering definitions and contexts. |
| **Custom (Std)** | **1.0x** | Baseline context for our specific domains. |
| **External (Vuln)** | **0.5x** | Downsample slightly to prevent `CVE` patterns from overwhelming other entities. |
| **External (Eng)** | **1.0x** | Keep standard to reinforce `DEVICE` and `MEASUREMENT` learning. |

## 4. Potential Risks & Mitigations

| Risk | Description | Mitigation |
| :--- | :--- | :--- |
| **Label Confusion** | `MEASUREMENT` (External) vs `UNIT_OF_MEASURE` (Custom). | **Reconciled**. We kept both. `MEASUREMENT` = Value ("100 psi"), `UNIT` = Unit ("psi"). |
| **Volume Imbalance** | External data is 100x larger. | **Oversampling** Custom data (3x) and **Downsampling** repetitive External data (e.g., CVE lists). |
| **Context Loss** | External data is often just sentence snippets. | Custom data provides **full-document context**, teaching the model *where* entities appear. |

## 5. Final Merge Strategy & Target Composition

**Decision**: We will create a balanced training set of **~61,300 documents** by capping the massive `CIRCL_vuln` dataset.

### Target Composition Table

| Dataset Group | Action | Est. Count | Rationale |
| :--- | :--- | :--- | :--- |
| **Custom Data** | **Keep 100%** | **1,300** | **The Gold Standard**. Contains our specific engineering intelligence, operational modes, and new entity categories. Weighted **3.0x** during training to ensure high impact. |
| **MITRE / APTNER** | **Keep 100%** | **~22,000** | **High-Value Threat Intel**. Provides critical coverage of TTPs, Threat Actors, and Campaigns. Essential for the "Security" aspect of the model. |
| **Electrical / CyNER** | **Keep 100%** | **~15,000** | **Domain-Relevant**. Aligns closely with our target sectors (Energy, Infrastructure). Provides strong engineering entity coverage. |
| **CIRCL_vuln** | **CAP at 3%** | **~15,000** | **Volume Control**. The full dataset (515k docs) is 90% repetitive CVE reports. Capping at 15k provides sufficient vulnerability examples without drowning out other signals. |
| **Others** | **Keep 100%** | **~8,000** | **Breadth**. ExploitDB, KEV, etc. provide necessary variety in vulnerability and exploit descriptions. |
| **TOTAL** | **MERGE** | **~61,300** | **Balanced & High Quality**. Fits comfortably in RAM (~12GB peak) while maximizing the influence of Custom Data. |

### Capping Logic
The `CIRCL_vuln` dataset contains over 500,000 documents, mostly short descriptions of CVEs. Merging this entirely would dilute the Custom Data to <0.2% of the corpus. By capping it at ~15,000 documents (randomly sampled), we reduce its dominance while still retaining its value for teaching the model about vulnerabilities.

### Weighting Logic
*   **Custom Gold (3.0x)**: Oversampled to force the model to pay attention to our specific engineering contexts.
*   **Standard (1.0x)**: Baseline weight for all other datasets.
*   **Result**: Custom Data effectively represents ~7-8% of the training signal, despite being only ~2% of the document count.

## 6. Execution Plan
1.  **Sample**: Randomly select 15,000 documents from `CIRCL_vuln`.
2.  **Aggregate**: Combine all other external datasets + Custom Data.
3.  **Shuffle**: Randomize the order to prevent training bias.
4.  **Output**: Generate final `train.spacy` and `dev.spacy` in `NER11_Gold_Standard/final_training_set/`.
