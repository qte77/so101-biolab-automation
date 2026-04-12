---
title: "Outlook: ELN, LIMS & Protocol Tool Integration"
purpose: Feasibility study for integrating eLabFTW, SiLA 2, PyLabRobot, and other tools into the workflow
authority: Research (INFORMATIONAL — not requirements)
created: 2026-04-12
updated: 2026-04-12
---

# Outlook: ELN, LIMS & Protocol Tool Integration

## Concept

The project handles the physical automation layer (arms, pipette, tool changer,
Bento, gantry, camera). The missing layers are experiment recording, reagent
inventory, protocol standardization, and device interoperability. This document
surveys tools that fill those gaps and evaluates their programmability.

## Architecture Vision

```text
+---------------------------------------------+
|  ELN (eLabFTW / openBIS)                    |  <- experiment records, inventory
+---------------------------------------------+
|  Protocol Layer (SiLA 2 / Autoprotocol)     |  <- machine-readable protocols
+---------------------------------------------+
|  Orchestrator (workflow.py)                  |  <- YOU ARE HERE
+---------------------------------------------+
|  Device Layer (arms, pipette, gantry, etc.) |  <- YOU ARE HERE
+---------------------------------------------+
|  Dashboard (server.py)                       |  <- YOU ARE HERE
+---------------------------------------------+
```

## ELN / LIMS Tools

### eLabFTW — Recommended

Open-source (GPLv3), self-hosted via Docker, REST API v2 with full OpenAPI spec.

| Aspect | Detail |
|--------|--------|
| Architecture | PHP/MySQL, Docker Compose deployment |
| API | REST v2, OpenAPI/Swagger, API key auth, no documented rate limits |
| Python clients | **elAPI** (Uni Heidelberg, v2.4.10, `uv add elapi`) — best DX. **elabapi-python** (official, v5.5.0, auto-generated from OpenAPI) — thin but current |
| Extensibility | No plugin system, no webhooks. Customization via Docker env vars and API |
| Docs | Good (docs.elabftw.net, Swagger UI for API exploration) |
| GitHub | 1,307 stars, 291 forks, actively maintained |

**Integration pattern with this project:**

| Lifecycle | Module | eLabFTW API Call |
|-----------|--------|-----------------|
| Pre-run | `workflow.py` pulls protocol | `GET /api/v2/experiments/{template_id}` |
| Pre-run | `pipette.py` checks reagent stock | `GET /api/v2/items?q=reagent_name` |
| During | `workflow.py` status events | `PATCH /api/v2/experiments/{id}` (append to body) |
| Post-run | `camera.py` plate image | `POST /api/v2/experiments/{id}/uploads` |
| Post-run | Volumes used | `PATCH /api/v2/items/{id}` (decrement stock) |
| Post-run | Dashboard results | `PATCH /api/v2/experiments/{id}` (status=completed) |

Implementation: an `ELNClient` adapter class wrapping `elapi`, called by the
workflow orchestrator at lifecycle hooks. Auth via API key in environment
variable (not YAML — secrets do not belong in config files).

### openBIS / pyBIS — Evaluate

| Aspect | Detail |
|--------|--------|
| Package | `pybis` v1.37.4, Python 3.6+, pip-installable |
| Capabilities | Full CRUD on experiments, samples, datasets, projects. Vocabulary/property management. File upload/download |
| Jupyter | First-class — designed for notebook workflows |
| Backed by | ETH Zurich, actively maintained |
| Docs | Adequate but academic-style |
| Best for | FAIR data management, Jupyter-driven experiment design |

### Benchling — Skip (Paywalled)

| Aspect | Detail |
|--------|--------|
| SDK | `benchling-sdk` v1.24.1, typed, fluent API |
| Access | **Enterprise plan required** for API access — not free for academics |
| Webhooks | Supported on Enterprise |
| Docs | Excellent (best in class) |
| Verdict | Best SDK quality, but paywalled. Not viable for open-source projects |

### SENAITE LIMS — Skip (Too Heavy)

| Aspect | Detail |
|--------|--------|
| API | `senaite.jsonapi` v2.6.0, RESTful JSON, CRU operations |
| Framework | Plone/Zope stack — heavy, steep learning curve |
| Docs | Sparse (11 stars, small community) |
| Verdict | ISO 17025 focus, Plone dependency is a significant adoption barrier |

### SciNote — Skip (Limited)

| Aspect | Detail |
|--------|--------|
| API | REST only, no Python SDK |
| Access | SaaS, free tier exists |
| Verdict | Basic LIMS, limited automation support |

## Protocol Standardization

### SiLA 2 — Evaluate for Device Interop

Standardization in Lab Automation — gRPC + Protocol Buffers standard for lab
device communication.

| Aspect | Detail |
|--------|--------|
| PyPI | `sila2` v0.14.0 (maintenance-only) — use **UniteLabs fork** instead |
| Custom servers | Define Feature Definition Language (FDL) XML, generate gRPC stubs, implement handlers. Can wrap any device |
| Integration | Each hardware module (`DualArmController`, `ElectronicPipette`, `BentoLab`) could expose a SiLA 2 Feature — making them discoverable and interoperable |
| Real-world OSS | Few public implementations. UniteLabs has examples. Standard is more adopted in pharma (closed-source) |
| Docs | Adequate for spec, thin for Python library |
| Used with | Opentrons OT-2, Franka Emika arms (production) |

### Autoprotocol — Skip (Dead)

| Aspect | Detail |
|--------|--------|
| Package | `autoprotocol-python` v10.3.0, **last release Apr 2023** |
| Status | Effectively abandoned (Strateos/Automata acquisition) |
| Scope | Protocol definition only (JSON AST). Execution required Strateos cloud lab |
| Verdict | Dead project. Not viable for new integrations |

## Data Pipeline & Analysis Tools

### PyLabRobot — Use (Custom Backend for SO-101)

Hardware-agnostic Python SDK for liquid handling robots.

| Aspect | Detail |
|--------|--------|
| Package | `pylabrobot` v0.2.1, 426 stars, 144 forks, MIT |
| Architecture | `LiquidHandler(backend=XXXBackend(), deck=deck)` — pluggable backends |
| Custom backends | Implement backend abstract class methods (setup, aspirate, dispense, move). Well-designed for extension |
| Supported hardware | Hamilton STAR/Vantage, Tecan EVO, Opentrons OT-2, plate readers, centrifuges, pumps, scales |
| 3D printer backends | **Not supported** — but backend architecture is pluggable enough to write one |
| Docs | Good (docs.pylabrobot.org, community forum) |
| Verdict | Write a custom backend for SO-101 arms to make them interoperable with the broader lab automation ecosystem |

### MLflow — Use If Needed

| Aspect | Detail |
|--------|--------|
| Package | `mlflow` v3.11.1, 25k+ stars, 60M+ monthly downloads |
| Wet-lab tracking | `log_param()` / `log_metric()` / `log_artifact()` are domain-agnostic. Track concentrations, temperatures, volumes, OD readings, yields |
| Verdict | Zero integration cost. Works well as experiment tracker without the ML parts |

### Frictionless Data — Nice to Have

Tabular data packaging with schema validation for CSV experiment results.
Standardizes output format.

## In-Repo Hardware Status

The project already has hardware integration for Bento Lab and electronic
pipettes, currently in stub mode pending protocol reverse engineering.

### Bento Lab (bento.bio)

| Aspect | Detail |
|--------|--------|
| Interface | BLE (Bluetooth Low Energy) + on-board click-wheel |
| Protocol | **Closed, undocumented** — no public API, SDK, or serial protocol |
| Firmware | Proprietary, closed-source. OTA updates via BLE/WiFi |
| Code in repo | Stub mode (`bento_lab.py`, 121 LOC). Config in `configs/bento_lab.yaml` |
| Path to control | BLE GATT sniffing (nRF Connect / Wireshark) — sniff app traffic, map GATT characteristics to commands |
| BOM note | "USB control TBD" |

### Electronic Pipettes (AELAB dPette 7016, DLAB dPette+)

| Aspect | Detail |
|--------|--------|
| Interface | USB (calibration-only software, no SDK) |
| Protocol | **Closed, undocumented** — 2 physical buttons for all operations |
| Code in repo | Stub mode (`ElectronicPipette` class in `pipette.py`). Config in `configs/pipette.yaml` |
| 3D scan | `hardware/scans/dpette/` (Revopoint MINI 2, 1:1 mm, PLY/STL) |
| Control paths (priority) | 1. USB reverse engineering (pyserial + USBREVue/Wireshark). 2. GPIO button bypass (optocoupler). 3. Mechanical button press (servo/second arm) |

### Digital Pipette v2 (DIY Alternative) — Functional

| Aspect | Detail |
|--------|--------|
| Interface | Arduino serial (fully documented) |
| Protocol | Open, published |
| Code | `digital-pipette-v2` (ac-rad, CC BY 4.0 + MIT) |
| Status | Functional backend in `pipette.py` |

## Summary: What to Use

| Priority | Tool | Why |
|----------|------|-----|
| **Use** | eLabFTW + elAPI | Open-source ELN, Docker-native, mature REST API, `uv`-installable |
| **Use** | PyLabRobot (custom backend) | Make SO-101 arms interoperable with lab automation ecosystem |
| **Use if needed** | MLflow | Zero-friction experiment tracking |
| **Evaluate** | openBIS / pyBIS | FAIR data, Jupyter-native — heavier than eLabFTW |
| **Evaluate later** | SiLA 2 (UniteLabs) | Device interop standard — overhead for a two-arm setup now |
| **Skip** | Benchling | Enterprise paywall |
| **Skip** | Autoprotocol | Dead project |
| **Skip** | SENAITE | Plone dependency too heavy |

## Quick Refs

| Ref | URL |
|-----|-----|
| eLabFTW docs | <https://doc.elabftw.net/> |
| eLabFTW API v2 spec | <https://doc.elabftw.net/api.html> |
| elabapi-python (official) | <https://github.com/elabftw/elabapi-python> |
| elAPI (Uni Heidelberg) | <https://github.com/uhd-urz/elAPI> |
| NIST eLabFTW Python API | <https://pages.nist.gov/elabftw-python-api/> |
| openBIS / pyBIS | <https://openbis.ch/> |
| Benchling SDK docs | <https://docs.benchling.com/> |
| SENAITE LIMS | <https://www.senaite.com/> |
| SciNote API | <https://www.scinote.net/product/integrations-and-api/> |
| SiLA 2 standard | <https://sila-standard.com/standards/> |
| sila2 (PyPI) | <https://pypi.org/project/sila2/> |
| SiLA Python (UniteLabs, GitLab) | <https://sila2.gitlab.io/sila_python/> |
| Autoprotocol | <https://www.autoprotocol.org/> |
| autoprotocol-python | <https://github.com/autoprotocol/autoprotocol-python> |
| PyLabRobot (GitHub) | <https://github.com/PyLabRobot/pylabrobot> |
| PyLabRobot docs | <https://docs.pylabrobot.org/> |
| PyLabRobot paper (PMC) | <https://pmc.ncbi.nlm.nih.gov/articles/PMC10369895/> |
| MLflow | <https://mlflow.org/> |
| Frictionless Data | <https://frictionlessdata.io/> |
| Bento Bio | <https://www.bento.bio/> |
| Digital Pipette v2 (ac-rad) | <https://github.com/ac-rad/digital-pipette-v2> |
| Hackable Syringe Pump | <https://github.com/kjiang8/Hackable-Syringe-Pump> |
| Poseidon syringe pumps | <https://github.com/pachterlab/poseidon> |
| GormleyLab Integra pipette | <https://github.com/GormleyLab/Pipette-Liquid-Handler> |
| Opentrons OT-3 firmware | <https://github.com/Opentrons/ot3-firmware> |
| USBREVue (USB reverse engineering) | <https://github.com/wcooley/usbrevue> |
