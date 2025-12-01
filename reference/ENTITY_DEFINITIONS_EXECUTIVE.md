# NER11 Entity Definitions - Executive Summary
**Target Audience**: Executives, Program Managers, Stakeholders
**Date**: 2025-11-25

This document explains the **Strategic Value** of the entity categories tracked by the NER11 Gold Standard Model.

---

## 1. Psychometrics (The "Human Layer")
**Why we track it**: Cyber attacks are human-driven. Understanding the attacker's mindset (and the defender's biases) allows for predictive defense.

*   **`COGNITIVE_BIAS`**: Mental shortcuts that lead to errors (e.g., "Confirmation Bias" leading an analyst to ignore contradictory evidence).
*   **`PERSONALITY_TRAIT`**: Characteristics that predict behavior (e.g., "Narcissism" in an insider threat, or "Conscientiousness" in a reliable admin).
*   **`LACANIAN_DISCOURSE`**: Advanced psychoanalytic patterns used to profile the deep motivations of APT groups or nation-state actors.

## 2. Critical Infrastructure (The "Physical Layer")
**Why we track it**: Cyber attacks now have kinetic consequences. We must map the digital threat to the physical asset it controls.

*   **`SECTOR`** & **`FACILITY`**: The target environment (e.g., "Water Treatment Plant", "Energy Grid").
*   **`SCADA_SYSTEM`**: The industrial control systems that manage physical processes (e.g., "PLC", "HMI").
*   **`PROTOCOL`**: The language machines speak (e.g., "MODBUS", "DNP3"). Identifying these allows us to detect anomalous commands.

## 3. Technical Cyber Threat (The "Attack Layer")
**Why we track it**: This is the core of Cyber Threat Intelligence (CTI). We must identify the *who*, *what*, and *how* of an attack.

*   **`THREAT_ACTOR`**: The adversary (e.g., "APT28", "Lazarus Group").
*   **`TTP` (Tactics, Techniques, Procedures)**: The specific methods used (e.g., "Spearphishing", "SQL Injection").
*   **`MALWARE`**: The weaponized code (e.g., "WannaCry", "Cobalt Strike").
*   **`INDICATOR`**: The digital fingerprints left behind (e.g., IP addresses, Hashes).

## 4. Vulnerability & SBOM (The "Risk Layer")
**Why we track it**: You can't defend what you don't know you have. Supply Chain attacks are the new norm.

*   **`CVE` (Common Vulnerabilities and Exposures)**: Known security flaws.
*   **`SBOM` (Software Bill of Materials)**: The ingredients list of your software. Tracking `SOFTWARE_COMPONENT` allows us to instantly know if we are affected by a library flaw (like Log4j).
*   **`CWE` (Common Weakness Enumeration)**: The underlying coding errors.

## 5. RAMS & Safety (The "Consequence Layer")
**Why we track it**: In industrial environments, "Security" equals "Safety". A cyber breach can cause an explosion or derailment.

*   **`HAZARD`**: A potential source of physical harm (e.g., "Overpressure", "Toxic Leak").
*   **`FAILURE_MODE`**: How a system breaks (e.g., "Valve Stuck Open").
*   **`SAFETY_INTEGRITY_LEVEL` (SIL)**: The required reliability of a safety function.

## 6. Economic & Organizational (The "Business Layer")
**Why we track it**: Cyber risk is business risk. We must quantify the impact in dollars and reputation.

*   **`FINANCIAL_IMPACT`**: The cost of an incident (e.g., "$5 Million Ransom").
*   **`REPUTATIONAL_THREAT`**: Damage to brand trust.
*   **`ROLE`**: The people involved (e.g., "CISO", "System Admin").

---

**Summary**:
The NER11 Model does not just "find words". It builds a **Holistic Digital Twin** of the cyber-physical environment, linking the **Attacker's Mind** (Psychometrics) to the **Physical Asset** (Infrastructure) and the **Business Impact** (Economics).
