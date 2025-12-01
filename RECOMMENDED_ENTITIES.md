# Recommended Entity Additions (Expanded)

Based on a deeper analysis of the `MISSING_CONCEPTS_REPORT.md`, the following categories and terms are recommended to significantly broaden the model's understanding of the **Operational**, **Engineering**, and **Process** domains.

## 1. Operational Modes & States
*   **`OPERATION_MODE`**: (New) - Captures the *state* of a system, critical for ICS/SCADA.
    *   *Terms*: "Manual", "Automatic", "Remote", "Local", "Real-time", "Continuous", "Offline", "Online".
*   **`ACCESS_STATE`**: (New) - Describes permission levels and access types.
    *   *Terms*: "Authorized", "Unauthorized", "Privileged", "Restricted", "Public", "Private".
*   **`SYSTEM_LIFECYCLE`**: (New) - Describes the age or phase of technology.
    *   *Terms*: "Legacy", "Modern", "Obsolete", "New", "Existing", "Proposed".

## 2. System Attributes & Qualities
*   **`SYSTEM_ATTRIBUTE`**: (New) - Key descriptors of system architecture.
    *   *Terms*: "Redundant", "Distributed", "Centralized", "Integrated", "Digital", "Analog", "Wireless", "Wired".
*   **`PERFORMANCE_METRIC`**: (New) - Qualitative performance descriptors.
    *   *Terms*: "High", "Medium", "Low", "Critical", "Stable", "Unstable", "Peak", "Average".
*   **`DATA_FORMAT`**: (New) - File types and data structures found in logs/configs.
    *   *Terms*: "JSON", "XML", "CSV", "Binary", "Text", "Log", "Configuration", "PCAP".

## 3. Engineering & Physical
*   **`FREQUENCY`**: (185) - RF and CPU specs.
    *   *Terms*: "MHz", "Hz", "GHz", "kHz".
*   **`UNIT_OF_MEASURE`**: (New) - Physical measurements.
    *   *Terms*: "MW" (Megawatt), "kV" (Kilovolt), "Gbps", "Mbps", "PSI", "V", "A", "RPM".
*   **`HARDWARE_COMPONENT`**: (125) - Granular hardware parts.
    *   *Terms*: "CPU", "Memory", "RAM", "LED", "USB", "RFID", "Filter", "Battery", "Power Supply", "Chassis".
*   **`CONNECTION_TYPE`**: (New) - Physical or logical connections.
    *   *Terms*: "Ethernet", "Fiber", "Copper", "Serial", "USB", "Bluetooth", "Wi-Fi".

## 4. Process, Verification & Compliance
*   **`VERIFICATION_ACTIVITY`**: (New) - Critical for "Audit" and "Compliance" contexts.
    *   *Terms*: "Validation", "Verification", "Testing", "Audit", "Review", "Assessment", "Inspection", "Check".
*   **`PROCESS_ACTION`**: (New) - Verbs describing lifecycle actions.
    *   *Terms*: "Integration", "Migration", "Deployment", "Installation", "Configuration", "Maintenance", "Update", "Patching".
*   **`REGULATORY_CONCEPT`**: (New) - Abstract regulatory terms.
    *   *Terms*: "Compliance", "Regulation", "Standard", "Requirement", "Guideline", "Policy", "Mandate".

## 5. Cybersecurity & Threat Specifics
*   **`CRYPTOGRAPHY`**: (264) - Encryption details.
    *   *Terms*: "TLS", "SSL", "AES-256", "RSA", "SHA-256", "Encryption", "Hashing", "MFA", "PKI", "Certificate".
*   **`SECURITY_TOOL`**: (225) - Specific tools used by Red/Blue teams.
    *   *Terms*: "Kali Linux", "Metasploit", "Cobalt Strike", "EDR", "SIEM", "IDS", "IPS", "Firewall", "VPN", "Proxy".
*   **`THREAT_GROUP`**: (New) - Specific actor names.
    *   *Terms*: "Volt Typhoon", "APT28", "APT29", "Lazarus", "Sandworm", "VOLTZITE", "GRAPHITE".
*   **`ATTACK_TYPE`**: (145) - Specific attack vectors.
    *   *Terms*: "DDoS", "Phishing", "Spear Phishing", "Man-in-the-Middle", "Injection", "Tampering", "Spoofing".

## 6. Vendors & Organizations
*   **`VENDOR_NAME`**: (New) - Distinct from generic "Organization".
    *   *Terms*: "Siemens", "Honeywell", "Schneider Electric", "Rockwell Automation", "Alstom", "Microsoft", "Cisco", "Dragos", "CrowdStrike".

## Summary of Expansion
This expands the recommendation from ~7 categories to **18 distinct categories**, covering:
1.  **Physics/Hardware**: Units, Components, Connections.
2.  **Logic/State**: Modes, Access, Lifecycle.
3.  **Process**: Verification, Actions, Compliance.
4.  **Cyber**: Crypto, Tools, Groups, Attacks.
5.  **Data**: Formats, Attributes.

**Do you approve adding these 18 categories and their associated terms to the Master Entity List?**
