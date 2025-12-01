# NER11 Taskmaster: Data Enhancement Runbook
**Status**: READY FOR EXECUTION
**Objective**: Systematically enhance all 15 "Weak" sectors in the Custom Corpus using **Gemini Deep Research** methodology.
**Target**: Achieve a **200% improvement** in data quality per sector. Continue research until saturation of high-quality engineering and operational data is reached.

---

## 1. The Protocol (Gemini Deep Research)
**ANY AGENT** picking up this task must follow this strict **Deep Research** protocol. This goes beyond simple web searches; it requires multi-perspective analysis and persistent digging for engineering-grade details.

### Core Philosophy: "Multi-Agent, Multi-Perspective"
Do not rely on a single search query. Approach each sector from multiple angles simultaneously:
1.  **The Architect**: Searches for facility designs, blueprints, and layouts.
2.  **The Engineer**: Searches for equipment manuals, SCADA protocols, and device specifications.
3.  **The Operator**: Searches for standard operating procedures (SOPs), safety manuals, and incident reports.
4.  **The Auditor**: Searches for compliance checklists, regulatory fines, and vulnerability assessments.

### Step 1: Deep Research (Iterative & Parallel)
Use `search_web` with complex, multi-part queries designed to unearth "Infrastructure & Operations" details.

**Focus Areas (The "Infrastructure" Layer)**:
*   **Equipment**: Specific vendors, models, firmware versions, PLCs, RTUs, sensors.
*   **Vendors**: Major suppliers, integrators, service providers for that sector.
*   **Processes**: Chemical formulas, manufacturing steps, water treatment cycles, fuel refinement flows.
*   **Operations**: Shift logs, maintenance schedules, emergency shutdown procedures.
*   **Architecture**: Network diagrams, physical facility layouts, zoning, perimeter security.
*   **Data Flow**: Protocols (Modbus, DNP3, HL7), signal types, telemetry requirements.
*   **Facility Types**: Specific variations (e.g., "Run-of-river dam" vs. "Pumped storage").
*   **Metrics**: KPIs, pressure limits, voltage ratings, flow rates, temperature thresholds.
*   **Locations**: Major hubs, strategic reserves, interconnection points.

**Query Examples (Deep & Specific)**:
*   `"[Sector] facility detailed design specifications pdf"`
*   `"[Sector] SCADA system architecture diagram and vendor list"`
*   `"[Sector] operational maintenance schedule and safety protocols"`
*   `"[Sector] industrial control system vulnerability assessment report technical"`
*   `"[Sector] equipment procurement list and technical specifications"`

### Step 2: The "200% Quality" Filter
**DO NOT STOP** until you have found deep, technical content.
*   **REJECT**:
    *   Generic overviews ("What is a dam?").
    *   Marketing fluff ("Why we are the best").
    *   High-level policy without technical details.
*   **ACCEPT (Gold Standard)**:
    *   **Detailed Designs**: Documents showing how things are built.
    *   **Equipment Manuals**: Real specs for real machines.
    *   **Process Flows**: Step-by-step operational guides.
    *   **Architecture Diagrams**: Visuals or descriptions of system layouts.
    *   **Data Tables**: Lists of chemicals, ports, protocols, or metrics.

### Step 3: Ingestion & Conversion
*   Use `read_url_content` to fetch the text.
*   **Clean the Text**: Remove navigation menus, footers, and copyright boilerplate.
*   **Save File**:
    *   **Path**: `NER11_Gold_Standard/custom_data/source_files/[Sector_Name]/[Descriptive_Filename].md`
    *   **Format**: Markdown.

### Step 4: Validation
*   Verify the file is saved.
*   Log the addition in `NER11_BLOTTER.md`.

---

## 2. Target List (Sprint 1: Deep Research & Enhancement)
**Scope**: All 15 Sectors (excluding Energy).
**Goal**: Saturate each sector with high-quality engineering data.

| Sector | Focus Areas (Examples) | Search Strategy Hints |
| :--- | :--- | :--- |
| **Water** | Pumps, Valves, SCADA, Chemicals (Chlorine, Fluoride) | `AWWA standards`, `water treatment plant design pdf`, `PLC logic for water distribution` |
| **Dams** | Turbines, Spillways, Sensors, Hydro-control systems | `USACE dam safety manual`, `hydroelectric turbine maintenance guide`, `dam failure mode analysis` |
| **Transportation** | Signaling, Ticketing, ATC, Pipeline gauges, Rail switches | `railway signaling circuits`, `airport baggage handling system specs`, `pipeline SCADA architecture` |
| **Nuclear** | Reactors, Cooling, Containment, Fuel Rods, Security | `PWR reactor coolant system design`, `nuclear power plant security plan template`, `radiation monitoring system specs` |
| **Financial** | SWIFT, ATM protocols, HFT algorithms, Datacenters | `ATM cash dispensing mechanism`, `FIX protocol specifications`, `banking datacenter tier standards` |
| **Commercial** | HVAC, Access Control, POS systems, Elevators | `BMS building management system protocols`, `casino surveillance system specs`, `retail POS network diagram` |
| **Manufacturing** | Robotics, Assembly Lines, CNC, PLCs, Conveyors | `automotive assembly line layout`, `industrial robot programming manual`, `CNC machine safety interlocks` |
| **Food/Ag** | Irrigation, Harvesters, Processing belts, Cold chain | `dairy processing plant P&ID`, `grain elevator control system`, `cold storage temperature monitoring` |
| **Healthcare** | MRI, Infusion Pumps, PACS, EHR, HVAC | `hospital medical gas system design`, `MRI machine installation guide`, `HL7 interface specifications` |
| **Emergency** | 911 Dispatch, Radio towers, Sirens, Fleets | `NG911 network architecture`, `P25 radio system design`, `EOC emergency operations center layout` |
| **Government** | Access cards, databases, voting machines, HVAC | `GSA building security standards`, `voting machine technical data package`, `federal building HVAC specs` |
| **Defense** | Radar, Logistics, Bases, Weapons systems (non-classified) | `military base utility infrastructure`, `logistics supply chain data model`, `radar system maintenance manual` |
| **IT/Telecom** | Towers, Fiber, Switches, Routers, 5G | `cell tower structural analysis`, `fiber optic splice closure specs`, `5G core network architecture` |
| **Communications** | Satellites, Broadcast, Cable, Internet Exchanges | `satellite ground station equipment`, `broadcast transmitter schematics`, `IXP network topology` |
| **Chemical** | Reactors, Mixers, Storage Tanks, Hazmat | `chemical plant P&ID`, `hazardous waste storage tank specs`, `batch reactor control strategy` |

---

## 3. Execution Log
*   [x] **Sprint 1: Deep Research Complete** (All 15 Sectors Enhanced)
