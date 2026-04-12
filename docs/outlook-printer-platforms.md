---
title: "Outlook: 3D Printers & CNC as Pipetting Platforms"
purpose: Feasibility study for repurposing used 3D printers and CNC machines as Cartesian liquid handlers
authority: Research (INFORMATIONAL — not requirements)
created: 2026-04-12
updated: 2026-04-12
---

# Outlook: 3D Printers & CNC as Pipetting Platforms

## Concept

Repurpose used/older 3D printers as Cartesian liquid-handling platforms.
Their existing 3-axis motion systems achieve sufficient accuracy for well-plate
work at a fraction of the cost of commercial liquid handlers. This complements
(not replaces) the SO-101 arms — arms handle dexterous tasks (tool changing,
Bento lid, complex manipulation), while a printer handles high-throughput
Cartesian pipetting (serial dilutions, plate-to-plate transfers).

## Existing Conversion Projects

### Actively Maintained (Code Public, Python API)

| Project | Base Platform | Python API | PyPI | Stars | License | Docs |
|---------|--------------|------------|------|-------|---------|------|
| Science Jubilee | Jubilee (CoreXY, Duet3D) | `Machine` class, Jupyter-native | `science-jubilee` v0.3.2 | 40 | MIT | Good (ReadTheDocs) |
| PyLabRobot | Hardware-agnostic | Pluggable backends | `pylabrobot` v0.2.1 | 426 | MIT | Good |
| Opentrons OT-2 | Custom (ex-3D printer) | Protocol API | `opentrons` v9.0.0 | 498 | Apache-2.0 | Excellent |
| PipetBot-A8 | Anet A8 (Marlin) | `pyotronext` (serial G-code) | No | — | Unknown | Good (dedicated site) |

### Paper-Only (No Public Repo)

| Project | Cost | Key Result | Code |
|---------|------|------------|------|
| PALH (Brown, 2024) | ~$400 | Validated qPCR, DNA extraction | No repo |
| MULA | ~700 EUR | <0.3% pipetting error, Hamilton syringe | Partial (Mendeley, CC BY-NC 3.0) |
| BioCloneBot | ~$400 | Ender 3 Pro conversion | GitHub (2 stars, C# only, dormant) |
| FINDUS | <$400 | Fully 3D-printed, <0.3% error | No repo |
| OTTO | ~$1,500 | OpenBuilds linear rails | No repo |
| PHIL | — | Miniature, fits on microscope stage | No repo |

## Printer Comparison

| Printer | Build Volume (mm) | Motion | Bed Moves? | Firmware | Used Price | 384-Well? |
|---------|-------------------|--------|------------|----------|------------|-----------|
| **Voron 2.4** | 250-350 cubed | **CoreXY** | **No (Z only)** | **Klipper** | $500-800 (kit) | **Yes** |
| Sovol SV03 | 350x350x400 | Cartesian | Yes (Y) | Marlin | $80-140 | Marginal |
| Anycubic i3 Mega | 210x210x205 | Cartesian | Yes (Y) | Marlin | $60-120 | No |
| Geeetech A30 | 320x320x420 | Cartesian | Yes (Y) | Marlin | $80-150 | No |
| Qidi X-Max | 300x250x300 | Cartesian | Yes (Y) | Marlin fork | $150-250 | Marginal |

**Critical distinction:** Bed-slingers move the bed in Y — moving liquid-filled
wells risks spillage and positional error. The Voron 2.4 keeps the bed
stationary in XY, which is essential for plate work.

### Reflashability

All six printers can be reflashed with open firmware. All expose USB serial
G-code (115200 baud). Qidi X-Max has a locked bootloader on some revisions
(community workarounds exist).

## Firmware Ecosystems

### Klipper + Moonraker (Voron 2.4)

- Python host (`klippy`) on Raspberry Pi, thin C firmware on MCU.
- **Custom Python plugins:** `klippy/extras/` directory (~134 modules).
- **G-code macros:** `[gcode_macro]` with Jinja2 templates and variables.
  Define `ASPIRATE`, `DISPENSE`, `MOVE_TO_WELL` as macros.
- **Moonraker API:** REST + WebSocket. `POST /api/printer/command` (G-code),
  `GET /api/printer/objects/query` (status). Real-time subscriptions.
- **Python client:** `moonraker-api` on PyPI (v2.0.6) — async WebSocket.
- **Docs:** Excellent (config reference, API docs at moonraker.readthedocs.io).

### Marlin + OctoPrint (Budget Printers)

- **Serial G-code:** 115200 baud, USB-serial via CH340/FTDI.
- **Python serial control:** `printrun.printcore` (PyPI, 2.6k stars).
- **OctoPrint REST API:** `/api/printer/command`, `/api/printer` (status).
  `octorest` Python client on PyPI.
- **Custom G-code:** Requires C++ source mod and recompile (not pluggable).
- **Docs:** Good (OctoPrint API docs excellent, Marlin is config-focused).

### Duet3D / RepRapFirmware (Science Jubilee)

- **HTTP API:** `POST /machine/code` (SBC) or `GET /rr_gcode` (standalone).
- **Object model:** `GET /machine/status` for full printer state.
- **Docs:** Good. Simpler than Moonraker for direct G-code but fewer
  subscription features.

## Conversion Approach

1. **Tool head:** Replace hotend with syringe pump or electronic pipette mount.
   Extruder stepper (E-axis) drives the plunger. 3D-printed adapters suffice.
2. **Bed:** Replace with plate holder (3D-printed or machined). Science Jubilee
   uses a 6-plate deck matching SBS/ANSI footprint (128x86 mm).
3. **Firmware:** Repurpose E-axis G-code (`G1 E` commands) for aspirate/dispense.
   Custom macros map volume to stepper steps.
4. **Calibration:** Home XY to plate corner fiducials; Z-probe to plate surface.
   Well offset tables from ANSI/SLAS 4-2004 standard.

## Accuracy Requirements

| Plate | Well Pitch | Well Diameter | Required XY Accuracy |
|-------|-----------|---------------|---------------------|
| 96-well | 9.0 mm | ~6.5 mm | +/-1.0 mm (comfortable) |
| 384-well | 4.5 mm | ~3.5 mm | +/-0.5 mm (tight) |

Typical 3D printer repeatability: ~300-500 um (96-well OK, 384-well marginal).
Voron 2.4 with CoreXY and linear rails: <100 um — meets 384-well comfortably.

## Cost Comparison

| Approach | Cost | Plate Support |
|----------|------|--------------|
| Used printer conversion (Ender 3, Sovol) | $325-700 | 96-well |
| Voron 2.4 build + conversion | $800-1,500 | 96 + 384-well |
| Science Jubilee (Filastruder kit) | ~$1,500-2,000 | 96 + 384 + tool changing |
| OpenBuilds custom (OTTO-style) | ~$1,500 | 96 + 384-well |
| Opentrons OT-2 | $6,000-10,000 | 96 + 384-well |
| Hamilton STAR/Vantage | $100,000+ | All formats |

## CNC Alternatives

| Platform | Frame | Cost | Rigidity | Suitability |
|----------|-------|------|----------|-------------|
| PrintNC | Steel tube | $800-1,200 | Excellent | Overkill — designed for milling forces |
| MPCNC | Conduit/printed | $300-500 | Low-Medium | Large community, less precise |
| Workbee | Aluminum extrusion | $600-1,000 | Good | Clean motion, good middle ground |

Trade-off: CNC frames are more rigid but lack ready-made electronics, firmware
ecosystem, and extruder stepper for pipette actuation.

## Integration with This Project

- **`PipetteConfig` / `ElectronicPipetteConfig`** models already define pipette
  parameters — same pipette, just mounted on a printer carriage.
- **`PlateLayout`** model (well positions, pitch, origin offsets) maps directly
  to G-code well coordinates — the YAML config is already there.
- **Software layer:** Replace arm IK with G-code generation. PyLabRobot
  provides a hardware-agnostic Python API that could sit alongside `workflow.py`.
- **Complementary roles:** Arms handle dexterous tasks. Printer handles
  high-throughput Cartesian pipetting.

## Voron 2.4 as Standout Candidate

- Stationary bed — no liquid sloshing.
- CoreXY rigidity — aluminum extrusion + linear rails, <1% dimensional error.
- Klipper firmware — Python-based, trivial to add custom macros.
- Quad gantry leveling — automatic bed tramming for consistent Z.
- No existing Voron lab automation project found — this would be novel.

## Quick Refs

| Ref | URL |
|-----|-----|
| Science Jubilee (GitHub) | <https://github.com/machineagency/science-jubilee> |
| PyLabRobot (GitHub) | <https://github.com/PyLabRobot/pylabrobot> |
| PyLabRobot docs | <https://docs.pylabrobot.org/> |
| Opentrons (GitHub) | <https://github.com/Opentrons/opentrons> |
| Opentrons API docs | <https://docs.opentrons.com/> |
| PipetBot-A8 | <https://derandere.gitlab.io/pipetbot-a8/> |
| PALH paper (ScienceDirect) | <https://www.sciencedirect.com/science/article/pii/S2472630324001213> |
| BioCloneBot (HardwareX) | <https://www.hardware-x.com/article/S2468-0672(24)00010-5/fulltext> |
| ACS liquid handler paper | <https://pubs.acs.org/doi/10.1021/acs.jchemed.3c00855> |
| MULA (Printables) | <https://www.printables.com/model/1019242-mula-a-diy-3d-printed-pipetting-robot-enabling-acc> |
| FINDUS (SLAS) | <https://journals.sagepub.com/doi/10.1177/2472630319877374> |
| OTTO (Nature Sci. Reports) | <https://www.nature.com/articles/s41598-020-70465-5> |
| PHIL (Nature Comms) | <https://www.nature.com/articles/s41467-022-30643-7> |
| Digital Pipette v2 (ac-rad) | <https://github.com/ac-rad/digital-pipette-v2> |
| Voron Design | <https://vorondesign.com/voron2.4> |
| Voron 2.4 review (3DPI) | <https://3dprintingindustry.com/news/review-ldo-voron-2-4-300-a-premium-high-speed-diy-3d-printer-236079/> |
| Sovol refurbished printers | <https://www.sovol3d.com/products/sovol-used-3d-printer> |
| Anycubic i3 Mega CNC mod | <https://www.printables.com/model/35905-anycubic-i3-mega-cnc-mod> |
| Klipper config reference | <https://www.klipper3d.org/Config_Reference.html> |
| Moonraker API docs | <https://moonraker.readthedocs.io/> |
| moonraker-api (PyPI) | <https://pypi.org/project/moonraker-api/> |
| printrun (PyPI) | <https://pypi.org/project/printrun/> |
| OctoPrint REST API | <https://docs.octoprint.org/en/master/api/> |
| ANSI/SLAS 4-2004 well positions | <https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_4-2004_WellPositions.pdf> |
| PrintNC (GitHub) | <https://github.com/threedesigns/printNC> |
| r/Sovol (Reddit) | <https://www.reddit.com/r/Sovol/> |
