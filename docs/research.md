---
title: Research Findings
purpose: Community designs, academic papers, future vision (VLM, embodied AI, PCR use case)
authority: Research (INFORMATIONAL — not requirements)
sources: MakerWorld, Thingiverse, Printables, GitHub, arXiv, bioRxiv, Reddit, MakerForge, UZH, EPFL
created: 2026-03-27
updated: 2026-03-27
validated_links: 2026-03-27
---

# Research Findings: Enhancements & Good-to-Knows for so101-biolab-automation

## Key Finding: No SO-101 Pipette End Effector Exists

No community design for a pipette attachment specifically for SO-101. This is an original contribution opportunity.

## Hardware Enhancements (3D-Printed)

| Design | Source | Date | Relevance |
|--------|--------|------|-----------|
| [Parallel Gripper for SO-101](https://makerworld.com/en/models/1549112) | MakerWorld (energiazero.org) | 2025-06 | Direct SO-101 wrist replacement. Adapt jaws for pipette holding. CAD: [GrabCAD](https://grabcad.com/library/standard-open-so-101-arms-with-parallel-gripper-1) |
| [TPU Grip for SO-100/101](https://www.thingiverse.com/thing:7153144) | Thingiverse (NekoMaker) | 2025-09 | Compliant fingertips for smooth objects (pipette barrels, plates). |
| [Silicone Gripper Tip Mold](https://www.thingiverse.com/thing:7152864) | Thingiverse (NekoMaker) | 2025-09 | Cast silicone tips for delicate labware handling. |
| [Reinforced Trigger](https://www.printables.com/model/1323562) | Printables (Chitoku) | 2025-06 | Fixes leader arm trigger breakage. **Apply Loctite 242 to motor 5 screw.** |
| [Bambu-Optimized SO-101](https://makerworld.com/en/models/1399268) | MakerWorld (manfromwest) | 2025-05 | Best SO-101 print files for Bambu. Camera mount provisions. |
| [AB-SO-BOT](https://github.com/Mr-C4T/AB-SO-BOT) | GitHub (54 stars) | 2025 | Aluminium body upgrade with RealSense mounts. |
| [WH148 Leader Arm](https://www.thingiverse.com/thing:7041540) | Thingiverse (xuyuan) | 2025-05 | Cheaper potentiometer-based leader arm. |
| [SO-101 Fin-Ray Gripper](https://makerworld.com/en/models/2075813) | MakerWorld (GauravMM) | 2025-12 | Compliant gripper for delicate/oddly-shaped objects. TPU 95A. |
| [SO-101 Parallel Gripper](https://github.com/roboninecom/SO-ARM100-101-Parallel-Gripper) | GitHub (Robonine) | 2026-03 | 1.5kg payload, 100.5mm stroke, $76. Open-source STL + code. |
| [XLeRobot](https://github.com/Vector-Wangel/XLeRobot) | GitHub ([docs](https://xlerobot.readthedocs.io)) | 2025 | Dual SO-101 on mobile base (LeKiwi). $660. URDFs + ManiSkill sim. 600-1000g payload/arm. |

## Tool Changer Design

**Primary source: [Berkeley Passive Tool Changer](https://goldberg.berkeley.edu/pubs/CASE2018-ron-tool-changer-submitted.pdf)**
**Repo: [BerkeleyAutomation/RobotToolChanger](https://github.com/BerkeleyAutomation/RobotToolChanger)** (branch: `tool-changer`)

**What we reuse directly:**
- Design geometry: 10° truncated cone angle, 5N magnets, spring-loaded dowel pins
- 3-part architecture: robot-side adapter, tool-side base, parking housing
- STL reference: 3 dirs (robot component, tool component, tool housing) — adapt dimensions from ABB YuMi flange to SO-101 wrist flange
- Passive locking principle: no power, no data through the tool interface
- ArUco marker guidance idea from paper's failure analysis (positioning errors, not mechanism)

**What we adapt:**
- Flange interface: redesign robot-side adapter for SO-101 motor 5 horn mount (M3 screw pattern, ~25mm diameter)
- Tool parking rack: design for 3 tools side-by-side at fixed workspace position
- Cable routing: add flat flex cable channel for pipette power (not in Berkeley design)

**License note:** Berkeley repo has no stated license. Use paper's design principles and our own STL geometry.

## Open-Source Liquid Handling Projects

| Project | URL | License | Date | What We Reuse |
|---------|-----|---------|------|---------------|
| [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2) | GitHub | CC BY 4.0 + MIT | v2.0.0, 2025-11 | **Option A (DIY).** 5 STL parts, Arduino firmware, Python controller, Actuonix L16 actuator, full BOM. |
| [FINDUS](https://github.com/FBarthels/FINDUS) | GitHub | GPL-3.0 | 2020 ([paper](https://doi.org/10.1177/2472630319877374)) | Calibration procedure (<0.3% error). Tip-fit validation method. |
| [OTTO](https://github.com/DrD-Flo/OTTO) | GitHub | MIT | 2023 | Tip pickup geometry (insertion angle, force). Ejection mechanism. |
| [Sidekick](https://github.com/rodolfokeesey/Liquid-Handler) | GitHub | CERN-OHL-S v2 | 2022 ([paper](https://doi.org/10.1016/j.ohx.2022.e00319)) | SBS plate addressing geometry. 10µL solenoid pump alternative. |
| [GormleyLab](https://github.com/GormleyLab/Pipette-Liquid-Handler) | GitHub | MIT | 2025 | Bluetooth Integra pipette Python interface (`liquidhandler.py`). |
| [MULA](https://www.printables.com/model/1019242) | Printables | open | 2024 ([paper](https://doi.org/10.1016/j.ohx.2024.e00075)) | Gastight syringe mechanism. CAD on [Mendeley](https://data.mendeley.com/datasets/3m3t4f9ft3). |
| [OLA](https://docs.openlabautomata.xyz/) | Website | open | active | Community hub. Protocol sharing. |
| [PHIL](https://github.com/CSDGroup/PHIL) | GitHub | MIT | 2022 ([Nature Comms](https://www.nature.com/articles/s41467-022-30643-7)) | ETH Zurich. Personal pipetting robot. Tip management, media exchange, live-cell compatible. |
| [PyLabRobot](https://github.com/PyLabRobot/pylabrobot) | GitHub | Apache-2.0 | 2023 ([bioRxiv](https://www.biorxiv.org/content/10.1101/2023.07.10.547733)) | MIT Media Lab. Hardware-agnostic liquid handling. Already in our stack. Write SO-101 backend driver. |
| [OptoBot](https://github.com/nicolaegues/OptoBot) | GitHub | — | 2024 | OT-2 + Python for automated experimental optimization loops. Closed-loop observe→decide→pipette pattern. |
| [OT-2 Plate Handler](https://doi.org/10.26434/chemrxiv-2025-n95kk) | ChemRxiv | — | 2025 (Bolt et al.) | 3D-printed robotic claw for Opentrons OT-2. Plate gripping geometry + positioning tolerances reusable. |

## Bimanual SO-101 Support

**[AIDASLab/lerobot-so101-bimanual](https://github.com/AIDASLab/lerobot-so101-bimanual)** (2026-01, 5 stars) — Drop-in LeRobot fork with `bi_so101_follower`/`bi_so101_leader` types. Calibration, teleoperation, recording all work dual-arm. **Use this instead of patching upstream.**

## Commercial References

### Andrew+ (Waters/Andrew Alliance) — [UZH page](https://www.zmb.uzh.ch/en/Available-Systems/SamplePreparationInstruments/Andrew-%2C-The-Pipetting-Robot.html)

- Cartesian gantry + interchangeable electronic pipettes (single/8-channel)
- Modular "Domino" snap-in accessories (heater/shaker, cooled racks, tip racks)
- OneLab cloud protocol software (drag-and-drop)
- Lessons: modular workspace with fixed slot positions; separate pipettes by volume range; 8-channel head for 96-well efficiency

### Sartorius Electronic Pipettes — [product page](https://www.sartorius.com/en/products/pipetting/electronic-pipettes)

- Picus 2: single/multi-channel, Bluetooth, programmable protocols
- Future integration target for SO-101 (see Pipette Strategy section)

## Community Resources

- [MakerForge SO-101 guide](https://www.makerforge.tech/posts/seeed-so101/) — servo calibration, port detection, teleoperation setup
- [Seeed Studio SO-101 wiki](https://wiki.seeedstudio.com/lerobot_so100m/) — reComputer Jetson + SO-101 kits
- [PyLabRobot 2025 roadmap](http://discuss.pylabrobot.org/t/plr-dev-roadmap-2025-q1-q2/143) — extending to robotic arms (directly relevant)

## Known Hardware Issues

- **Gripper screw loosening** (motor 5) — apply Loctite 242/243 before long runs
- **USB disconnect during teleoperation** ([lerobot #3131](https://github.com/huggingface/lerobot/issues/3131)) — implement reconnect watchdog
- **Pipetting motion** should be decomposed into discrete phases for training (approach → insert tip → aspirate → move → dispense → eject)
- **50+ episodes minimum** per task, deliberate slow motions, 80k+ training steps

## Academic Papers (Most Actionable)

**What we reuse from papers:**
- **AutoBio**: open-source eval harness at `autobio-bench/AutoBio` — validate our policies against standard bio-lab tasks
- **DexMimicGen**: NVIDIA data amplification — 20 real demos → 2000 synthetic for ACT training
- **ArticuBot**: pre-trained fridge/door policy — zero-shot transfer for UC2, skip real fridge demos
- **InterACT/MoE-ACT**: replace vanilla ACT with inter-arm attention for bimanual pipetting
- **Tool-as-Interface**: collect pipetting demos from human video instead of robot teleoperation
- **Echo**: open-source force-feedback teleoperation — improve demo quality for tip press-fit
- **RoboCopilot**: human-in-the-loop correction loop — lab tech intervenes, corrections become training data
- **AIDASLab bimanual fork**: drop-in dual SO-101 support — `bi_so101_follower`/`bi_so101_leader` types

### ETH / EPFL Lab Automation (Swiss)

| Paper | Year | Institution | Key Finding |
|-------|------|-------------|-------------|
| [PHIL — Pipetting Helper Imaging Lid](https://www.nature.com/articles/s41467-022-30643-7) | 2022 | ETH Zurich (Dettinger et al., CSD Group) | Open-source personal pipetting robot. MIT license. 3D-printed + commercial parts. Live-cell incubation compatible. **Repo: [CSDGroup/PHIL](https://github.com/CSDGroup/PHIL)**. Reuse: tip management, media exchange protocols, compact form factor. |
| [SIMO — Microplate Handling via Vision + Touch](https://doi.org/10.3389/frobt.2024.1462717) | 2025 | EPFL (Scamarcio, Tan, Hughes, Stellacci) | Bi-manual mobile robot (ABB GoFa) with vision + tactile feedback for microplate handling. **1.2mm accuracy, ≥95% success rate.** Reuse: 3-stage localization (SLAM → fiducial → tactile), impedance control for plate grasping. Sets accuracy benchmark for our SO-101. |

### General Lab Automation

| Paper | Year | Key Finding |
|-------|------|-------------|
| [RoboCulture](https://arxiv.org/abs/2505.14941) | 2025 | Complete robotics platform for bio experiments (pipetting, plate handling). Aspuru-Guzik group (Toronto). |
| [AutoBio](https://arxiv.org/abs/2505.14030) | 2025 | Simulation benchmark for bio-lab tasks. Open-source eval harness at `autobio-bench/AutoBio`. |
| [MatteriX](https://arxiv.org/abs/2601.13232) | 2026 | Digital twin for chemistry lab. Sim-to-real for pipetting without wasting reagents. |
| [Microplate Handling Accuracy](https://www.biorxiv.org/content/10.1101/2023.12.29.573685v1) | 2024 | Quantifies positioning tolerance for 96-well plate grasping. Sets engineering targets. |
| [Open Liquid Handler](https://www.biorxiv.org/content/10.64898/2026.03.02.709168v1) | 2026 | Industry-grade open-source liquid handler. PyLabRobot-compatible (same author). |
| [Keyframe-Guided Rewards](https://arxiv.org/abs/2603.00719) | 2026 | RL reward shaping for long-horizon lab tasks. Aligns with ACT chunked actions. |
| [BioMARS](https://arxiv.org/abs/2507.01485) | 2025 | Multi-agent robot system for autonomous bio experiments. Dual-arm coordination patterns. |
| [Dual Demonstration for Chemical Automation](https://arxiv.org/abs/2506.11384) | 2025 | Teaches both end-effector AND jig operations simultaneously. Tool-change + substrate-handling. |
| [Cutting the Cord](https://arxiv.org/abs/2603.09051) | 2026 | GPU-accelerated bimanual mobile manipulation on LeRobot/XLeRobot. Untethered deployment. |

### Imitation Learning (ACT & Bimanual)

| Paper | Year | Key Finding |
|-------|------|-------------|
| [ALOHA/ACT](https://arxiv.org/abs/2304.13705) | 2023 | Our training framework. 50 demos/task, low-cost bimanual. |
| [LeRobot](https://arxiv.org/abs/2602.22818) | 2026 | Our stack's authoritative reference. ICLR 2026. |
| [ALOHA Unleashed](https://arxiv.org/abs/2410.13126) | 2024 | More data > bigger model. DeepMind validation of ACT ceiling. |
| [InterACT](https://arxiv.org/abs/2409.07914) | 2024 | Hierarchical attention for inter-arm dependencies. Better than vanilla ACT for bimanual. |
| [MoE-ACT](https://arxiv.org/abs/2603.15265) | 2026 | One multi-task model via MoE. Handles 5+ tasks without per-task training. |
| [DexMimicGen](https://arxiv.org/abs/2410.24185) | 2024 | 20 demos → 2000 synthetic. NVIDIA open-source. Solves data scarcity. |
| [X-IL](https://arxiv.org/abs/2502.12330) | 2025 | Systematic policy architecture comparison. Guide for ACT alternatives. |
| [Bi-ACT](https://arxiv.org/abs/2401.17698) | 2024 | Bilateral force-feedback ACT. Improves demo quality for contact-rich tasks (tip press-fit). |
| [FTACT](https://arxiv.org/abs/2509.23112) | 2025 | Force-torque aware ACT. F/T sensor in observation space for contact-aware policies. |
| [Bimanual ACT with Inter-Arm Coordination](https://arxiv.org/abs/2503.13916) | 2025 | ACT + inter-arm coordination module. Precise bimanual synchronization (AIST Japan). |

### Tool Use & Door Opening

| Paper | Year | Key Finding |
|-------|------|-------------|
| [Tool-as-Interface](https://arxiv.org/abs/2504.04612) | 2025 | Learn from human tool-use video, not robot demos. Reduces data cost. |
| [FUNCTO](https://arxiv.org/abs/2502.11744) | 2025 | One-shot tool manipulation. Generalizes across tool variants. |
| [ArticuBot](https://arxiv.org/abs/2503.03045) | 2025 | Universal door/fridge policy trained in sim. Zero-shot real transfer. |
| [UniDoorManip](https://arxiv.org/abs/2403.02604) | 2024 | Universal door policy (pull, push, sliding). Covers lab equipment. |

### Data Collection

| Paper | Year | Key Finding |
|-------|------|-------------|
| [YOTO](https://arxiv.org/abs/2501.14208) | 2025 | One-shot bimanual from video. Near-zero demo cost. |
| [Echo](https://arxiv.org/abs/2504.07939) | 2025 | Force-feedback teleoperation. Better demos for press-fit tasks. Open-source. |
| [RoboCopilot](https://arxiv.org/abs/2503.07771) | 2025 | Human-in-the-loop correction during execution. Interventions become training data. |
| [GELLO](https://arxiv.org/abs/2309.13037) | 2023 | Low-cost replica-arm teleoperation (UC Berkeley). Alternative to leader-follower. |
| [Taming VR Teleoperation](https://arxiv.org/abs/2508.14542) | 2025 | VR-based multi-task bimanual demo collection. Less operator fatigue than leader arm. |
| [Opening Articulated Structures](https://arxiv.org/abs/2402.17767) | 2024 | Real-world door/fridge opening without pre-mapped kinematics (UIUC, Saurabh Gupta). |

## Cross-Cutting Insights

1. **Data > model complexity** — 50+ demos per task, amplify with DexMimicGen
2. **Force feedback is the main gap** — SO-101 has no wrist F/T sensor; biggest reliability risk for pipette tip press-fit
3. **Sim-to-real works for fridge/door** — ArticuBot demonstrates zero-shot transfer; may not need real demos for UC2
4. **Decompose pipetting into phases** — approach, insert tip, aspirate, dispense, eject. Train per-phase or use keyframe rewards.
5. **Bimanual needs inter-arm attention** — vanilla ACT struggles with coupled coordination; use InterACT or MoE-ACT
6. **PyLabRobot backend driver** — writing one for SO-101 makes all existing protocols work on our arms
7. **8-channel pipette head** — 8x efficiency for 96-well work; design as a specialized end-effector

## Slicer CLI & Parametric CAD Research

**Problem:** CadQuery generates geometrically correct STLs but has no FDM awareness. Vertical empty rows, unsupported overhangs, and gravity failures are invisible until a print fails.

### OpenSCAD CLI

Mature, stable parametric CAD. `.scad` -> STL/SVG/DXF/PNG via CLI.

```bash
openscad -o out.stl input.scad                    # export STL
openscad -o out.svg --projection=ortho input.scad  # export SVG
openscad -D 'length=100' -o out.stl input.scad     # parametric override
openscad -p params.json -P set_name -o out.stl input.scad  # parameter file
```

- Install: `apt install openscad`, snap, flatpak, or AppImage
- CSG maps 1:1 from CadQuery: `box`->`cube`, `cylinder`->`cylinder`, `cut`->`difference()`, `revolve`->`rotate_extrude()`
- No printability validation (must pair with slicer)

### Slicer CLI Comparison

| Tool | CLI Maturity | Headless Linux | Overhang Detection | Notes |
|------|-------------|----------------|-------------------|-------|
| **PrusaSlicer** | Mature | Yes | Yes | `prusa-slicer --export-gcode model.stl --load config.ini`. Most stable. [Wiki](https://github.com/prusa3d/PrusaSlicer/wiki/Command-Line-Interface) |
| **Bambu Studio** | Modern | Yes (Docker avail) | Yes | `--slice`, `--orient`, `--arrange`, JSON config. Best error codes. [Wiki](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage) |
| **SuperSlicer** | Mature | Yes | Enhanced | PrusaSlicer fork with better overhang detection. [Docs](https://docs.superslicer.org/advanced-usage-guides/cmd-line-guide/) |
| **CuraEngine** | Stable | Yes | Limited | Pure engine, no GUI deps. JSON settings. [GitHub](https://github.com/Ultimaker/CuraEngine) |
| **OrcaSlicer** | **Broken** | **No** (GTK3 crashes) | Yes (when it works) | CLI shares GUI code, segfaults headless. [#2714](https://github.com/OrcaSlicer/OrcaSlicer/issues/2714), [#12277](https://github.com/OrcaSlicer/OrcaSlicer/issues/12277) |

**OrcaSlicer CLI root cause:** wxWidgets 3.1.7 (GTK3 backend) initializes display context even in CLI mode. Stack: `libslic3r` (core, decoupled) → `libslic3r_gui` (wxWidgets) → single binary. Fix paths: guard GTK3 init behind `DISPLAY` check, or build headless binary from `libslic3r` only. Fork lineage: Slic3r → PrusaSlicer → Bambu Studio → OrcaSlicer (all share `libslic3r` core).

**Recommendation:** PrusaSlicer CLI for validation (stable, proven). Keep slicer-agnostic so Bambu Studio or SuperSlicer can substitute.

### Closed-Loop 3D Printing

#### Human Loop (voice/text → print)

```
Human (voice/text) → LLM → OpenSCAD → STL → Slicer → Print
       ↑                                          |
       └── human inspects, describes fix ──────────┘
```

Human describes a part or modification in natural language (via CC `/voice` or text). LLM generates OpenSCAD, slicer validates, human inspects result and iterates.

#### Agent Loop (goal → autonomous design-print-inspect)

```
Goal/Task spec ──→ Agent ──→ OpenSCAD → STL → Slicer validate
                     ↑                              |
                     |                         Printer API (MQTT)
                     |                              ↓
                     |                         Camera (RTSP/JPEG)
                     |                              ↓
                     └── VLM analyzes print ←───────┘
                         Agent adjusts design/params
```

Agent receives a goal (e.g., "print a plate holder fitting SBS 127.76x85.48mm with 0.5mm clearance, PLA+, must pass printability check"). Autonomously:
1. Generates OpenSCAD from spec
2. Validates via slicer CLI
3. Sends GCode to printer via MQTT API
4. Monitors print via camera feed (RTSP/JPEG)
5. VLM (vision-language model) analyzes camera frames for defects
6. On failure: agent adjusts design/params, re-slices, reprints

**Bambu camera + printer API (enables agent feedback):**
- Built-in cameras: X1 (RTSP), A1/P1 (JPEG frames)
- Local MQTT: `<printer-ip>:8883`, topic `device/<serial>/report`
- Python: [`bambu-connect`](https://pypi.org/project/bambu-connect/), [`bambulabs-api`](https://pypi.org/project/bambulabs-api/)
- Cloud API: [`Bambu-Lab-Cloud-API`](https://github.com/coelacant1/Bambu-Lab-Cloud-API) (unofficial)

**Camera-based failure detection:**

| Tool | How | Printers |
|------|-----|----------|
| [Obico](https://github.com/TheSpaghettiDetective/obico-server) | Vision model, 30-60s intervals, auto-pause | OctoPrint, Klipper, Bambu |
| [OctoEverywhere Gadget](https://octoeverywhere.com/gadget) | Neural net trained on millions of prints | OctoPrint |
| [PrintWatch](https://plugins.octoprint.org/plugins/printwatch/) | AI video feed, auto-pause | OctoPrint |

**LLM/VLM agent loops for 3D printing:**

| Project | Architecture | Result |
|---------|-------------|--------|
| [LLM-3D Print](https://arxiv.org/abs/2408.14307) | Multi-agent: supervisor + VLM image reasoning + planner + executor → camera → corrects → reprints | 5x structural integrity, expert-level error ID |
| [Build Great AI](https://zenml.io/llmops-database/llm-powered-3d-model-generation-for-3d-printing) | Text → LLaMA/GPT/Claude → OpenSCAD → STL | Hours to minutes for design |
| [CADialogue](https://www.sciencedirect.com/science/article/abs/pii/S0010448525001678) | Multimodal LLM: text + speech + images → parametric CAD | Conversational CAD |

### XLeRobot Reference

[XLeRobot](https://github.com/Vector-Wangel/XLeRobot) — dual SO-101 mobile platform ($660, <4h assembly).

- Uses STEP + 3MF workflow (no code-generated CAD)
- Distributes STEP files for modification, STL/3MF for printing
- Addresses gravity/support via documentation + manual slicer orientation
- Z-axis scaling in slicer for fit adjustments (not in CAD)
- No automated printability checking
- Proves slicer-based workflow is viable for SO-101 ecosystem

### Validation Pipeline (planned)

```
OpenSCAD (.scad) ──→ STL ──→ PrusaSlicer CLI ──→ printability report
```

- OpenSCAD: parametric generator (reliable CLI, SVG via projection)
- PrusaSlicer: printability validator (optional, graceful fallback if unavailable)
- CadQuery: legacy reference in `hardware/cad/` (no longer used for generation)

## STL Files Plan

Add draft STL files to `hardware/stl/` for custom parts. Mark as experimental — these are starting points for iteration once hardware arrives.

| File | Status | Source/Approach |
|------|--------|----------------|
| `hardware/stl/README.md` | NEW | Index of all STL files with status (experimental/validated), print settings, notes |
| `hardware/stl/pipette_mount_so101.stl` | EXPERIMENTAL | Adapt SO-101 wrist flange → digital-pipette-v2 body clamp. Reference: [digital-pipette-v2 STL](https://github.com/ac-rad/digital-pipette-v2/tree/main/stl) for pipette body dimensions. |
| `hardware/stl/tool_dock_3station.stl` | EXPERIMENTAL | 3 parking slots side-by-side. Berkeley cone geometry (10° angle). Magnets for retention. Reference: [BerkeleyAutomation/RobotToolChanger](https://github.com/BerkeleyAutomation/RobotToolChanger/tree/tool-changer). |
| `hardware/stl/tool_cone_robot.stl` | EXPERIMENTAL | Female cone adapter for SO-101 wrist (motor 5 horn mount, M3 pattern). Berkeley design. |
| `hardware/stl/tool_cone_pipette.stl` | EXPERIMENTAL | Male cone base for pipette tool. Mates with robot-side cone. |
| `hardware/stl/tool_cone_gripper.stl` | EXPERIMENTAL | Male cone base for stock gripper. |
| `hardware/stl/tool_cone_hook.stl` | EXPERIMENTAL | Male cone base for fridge hook. |
| `hardware/stl/fridge_hook_tool.stl` | EXPERIMENTAL | Hook end-effector for fridge door handle. |
| `hardware/stl/96well_plate_holder.stl` | EXPERIMENTAL | SBS footprint (127.76 x 85.48 mm) with alignment pins. Reference: [Microplate Handling Accuracy paper](https://www.biorxiv.org/content/10.1101/2023.12.29.573685v1) for tolerance targets. |
| `hardware/stl/tip_rack_holder.stl` | EXPERIMENTAL | Holds standard pipette tip rack at fixed workspace position. |
| `hardware/stl/gripper_tips_tpu.stl` | EXPERIMENTAL | Compliant fingertips. Reference: [NekoMaker TPU grip](https://www.thingiverse.com/thing:7153144). Print in TPU 95A. |

**Print settings:** PLA+ default, 0.4mm nozzle, 0.2mm layer, 15% infill. TPU 95A for gripper tips only.

**Note:** STL files generated programmatically (OpenSCAD or CadQuery) are preferred over manual CAD — reproducible, parametric, version-controlled. If using FreeCAD/Fusion360, commit the source file alongside the STL.

## Target Application: PCR Master Mix Preparation

**First real use case:** Automated PCR plate setup.

- **Accuracy target:** ±1-3 µL per well
- **Master mix:** 1.1x overage (e.g., for 96 reactions: prepare 106 reactions worth)
- **Typical volumes:** 20-25 µL total per well (15-20 µL master mix + 2-5 µL template)
- **Workflow:** Prepare 1.1x master mix in trough → distribute to 96-well PCR plate → add template per well → seal plate

**PCR plate setup sequence (UC1 extension):**
1. Arm A equips pipette, aspirates master mix from trough
2. Dispense 20 µL per well across plate (uc1_full_plate or uc1_row)
3. Arm A or B adds template DNA per well (different source per well or strip tube)
4. Arm swaps to gripper, moves plate to thermocycler (fridge-like door operation)

**Why ±1-3 µL is achievable:**
- [FINDUS](https://github.com/FBarthels/FINDUS) achieves <0.3% error with 3D-printed mechanics
- Digital-pipette-v2 uses Actuonix L16 linear actuator (0.05mm resolution over 50mm stroke)
- At 20 µL target: ±3 µL = ±15% tolerance — well within DIY capability
- At 200 µL master mix aliquots: ±3 µL = ±1.5% — easily achievable

## Pipette Strategy: DIY → Electronic → Autonomous

**Not locked to one pipette type.** The architecture supports multiple pipette backends:

| Option | Type | Control | Cost | Status |
|--------|------|---------|------|--------|
| [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2) | DIY syringe | Arduino serial | ~$95 | Available now (v2.0.0, 2025-11) |
| [Sartorius Picus 2](https://www.sartorius.com/en/products/pipetting/electronic-pipettes) | Commercial electronic | Bluetooth/serial | ~$800-2000 | Future — see [GormleyLab Python interface](https://github.com/GormleyLab/Pipette-Liquid-Handler) |
| [Integra VIAFLO](https://www.integra-biosciences.com/global/en/electronic-pipettes) | Commercial electronic | Bluetooth | ~$1000-3000 | Future — 8/12-channel for 96-well efficiency |
| Custom 8-channel head | DIY multi-channel | Arduino/stepper | ~$200 | Future — 8x efficiency for 96-well |

**`src/biolab/pipette.py` is already abstracted** — `aspirate(volume)`, `dispense(volume)`, `eject_tip()`. Adding a Sartorius/Integra backend is a new class implementing the same interface.

## Future Vision: VLM + Embodied AI for Hands-Off Autonomous Operation

### Operation Modes (Progressive)

```
Phase 1 (current)    → Stub mode, coordinate commands, remote dashboard
Phase 2 (hardware)   → Teleoperation + ACT policy training, in-situ operator
Phase 3 (remote)     → Remote-controlled via dashboard, human oversight
Phase 4 (vision)     → Wrist camera visual servoing, closed-loop correction
Phase 5 (autonomous) → VLM task planning + embodied execution, long-running unattended
```

### Why VLM + Embodied AI Is Necessary for Phase 4-5

- **Sub-mm alignment**: SO-101 open-loop repeatability (~1-2mm) insufficient for tip press-fit. Visual servoing closes the gap.
- **Meniscus detection**: Liquid level tracking during aspiration requires real-time vision.
- **Drift compensation**: Plate/rack positions shift during long runs. Can't rely on fixed coordinates.
- **Tool verification**: Confirm tip attached, tool engaged, plate seated — visual confirmation.
- **Task planning**: "Pipette row A with 25µL from reagent in fridge" → decompose into sub-tasks autonomously.
- **Error recovery**: Detect dropped tip, missed well, spill — re-plan and retry without human.

### Key Technologies

| Technology | Purpose | Reference |
|------------|---------|-----------|
| Real-time VLM | Task planning from natural language + visual scene understanding | [OpenVLA](https://arxiv.org/abs/2406.09246) (2024), [RT-2](https://arxiv.org/abs/2307.15818) (2023) |
| Embodied AI policy | End-to-end visuomotor control (camera → joint actions) | ACT/LeRobot (in stack), [π0](https://arxiv.org/abs/2410.24164) (Physical Intelligence, 2024) |
| Visual servoing | Sub-mm tip/well alignment from wrist camera | OpenCV + ArUco, or learned visual features |
| Force estimation | Tip press-fit without F/T sensor | [Bi-ACT](https://arxiv.org/abs/2401.17698), [FTACT](https://arxiv.org/abs/2509.23112) |
| Human-in-the-loop | Remote operator corrects policy; corrections become training data | [RoboCopilot](https://arxiv.org/abs/2503.07771) (2025) |
| Sim-to-real | Train in simulation, deploy zero-shot | [AutoBio](https://arxiv.org/abs/2505.14030), [MatteriX](https://arxiv.org/abs/2601.13232), [LeIsaac](https://huggingface.co/docs/lerobot/envhub_leisaac) |
| Data amplification | 20 real demos → 2000 synthetic | [DexMimicGen](https://arxiv.org/abs/2410.24185) (NVIDIA, open-source) |

### Long-Running Autonomous Execution

For unattended multi-hour runs (e.g., 96-well plate with replicates, overnight incubation cycles):

- **Watchdog**: SafetyMonitor already parks arms on heartbeat timeout (5s)
- **Remote dashboard**: WebSocket commands for pause/resume/e-stop from anywhere
- **State persistence**: Log every aspirate/dispense to a run journal (well, volume, timestamp)
- **Error budget**: Define acceptable failure rate (e.g., ≤2 missed wells per plate) before auto-abort
- **Checkpoint/resume**: If interrupted, resume from last successful well (journal-based)

### Hardware Additions for Phase 4-5

- High-res wrist cameras (in BOM: 32x32mm UVC modules)
- Overhead camera with ArUco workspace calibration
- Optional: depth camera ([RealSense D405 mount](https://github.com/TheRobotStudio/SO-ARM100#5-wristmount-cameras)) for 3D tip tracking
- Optional: wrist F/T sensor for contact-aware manipulation

## Recommended Next Actions (When Hardware Arrives)

1. Use [AIDASLab bimanual fork](https://github.com/AIDASLab/lerobot-so101-bimanual) for dual-arm setup
2. Apply Loctite 242 to motor 5 screws on all arms
3. Print [reinforced trigger](https://www.printables.com/model/1323562) for leader arm
4. Print [parallel gripper](https://makerworld.com/en/models/1549112) as pipette holder base
5. Port Berkeley tool changer cone to SO-101 wrist dimensions
6. Record 50 episodes per task using decomposed motion phases
7. Train ACT via LeRobot; evaluate on AutoBio benchmark
8. Implement USB watchdog for long-run stability
