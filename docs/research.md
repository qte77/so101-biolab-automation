---
title: Research — Prior Art & Literature
purpose: Community designs, academic papers, open-source projects, and cross-cutting insights for SO-101 biolab automation
authority: Research (INFORMATIONAL — not requirements)
sources: MakerWorld, Thingiverse, Printables, GitHub, arXiv, bioRxiv, Reddit, MakerForge, UZH, EPFL
created: 2026-03-27
updated: 2026-04-12
---

# Research: Prior Art & Literature

## Related Docs

| Topic | Doc |
|-------|-----|
| Hardware inventory & reverse engineering | [outlook-integrations.md](outlook-integrations.md) |
| Pipetting platforms (3D printers, CNC) | [outlook-printer-platforms.md](outlook-printer-platforms.md) |
| Ceiling-mounted SO-101 | [outlook-ceiling-rail.md](outlook-ceiling-rail.md) |
| CAD, slicers, simulation | [hardware/cad-tooling.md](hardware/cad-tooling.md) |
| PCR use case & acceptance criteria | [UserStory.md](UserStory.md) |
| Future vision & roadmap | [roadmap.md](roadmap.md) |

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

- Design geometry: 10 deg truncated cone angle, 5N magnets, spring-loaded dowel pins
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
| [Sidekick](https://github.com/rodolfokeesey/Liquid-Handler) | GitHub | CERN-OHL-S v2 | 2022 ([paper](https://doi.org/10.1016/j.ohx.2022.e00319)) | SBS plate addressing geometry. 10uL solenoid pump alternative. |
| [GormleyLab](https://github.com/GormleyLab/Pipette-Liquid-Handler) | GitHub | MIT | 2025 | Bluetooth Integra pipette Python interface (`liquidhandler.py`). |
| [MULA](https://www.printables.com/model/1019242) | Printables | open | 2024 ([paper](https://doi.org/10.1016/j.ohx.2024.e00075)) | Gastight syringe mechanism. CAD on [Mendeley](https://data.mendeley.com/datasets/3m3t4f9ft3). |
| [OLA](https://docs.openlabautomata.xyz/) | Website | open | active | Community hub. Protocol sharing. |
| [PHIL](https://github.com/CSDGroup/PHIL) | GitHub | MIT | 2022 ([Nature Comms](https://www.nature.com/articles/s41467-022-30643-7)) | ETH Zurich. Personal pipetting robot. Tip management, media exchange, live-cell compatible. |
| [PyLabRobot](https://github.com/PyLabRobot/pylabrobot) | GitHub | Apache-2.0 | 2023 ([bioRxiv](https://www.biorxiv.org/content/10.1101/2023.07.10.547733)) | MIT Media Lab. Hardware-agnostic liquid handling. Write SO-101 backend driver ([#63](https://github.com/qte77/so101-biolab-automation/issues/63)). |
| [OptoBot](https://github.com/nicolaegues/OptoBot) | GitHub | — | 2024 | OT-2 + Python for automated experimental optimization loops. Closed-loop observe-decide-pipette pattern. |
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
- Future integration target for SO-101

## Community Resources

- [MakerForge SO-101 guide](https://www.makerforge.tech/posts/seeed-so101/) — servo calibration, port detection, teleoperation setup
- [Seeed Studio SO-101 wiki](https://wiki.seeedstudio.com/lerobot_so100m/) — reComputer Jetson + SO-101 kits
- [PyLabRobot 2025 roadmap](http://discuss.pylabrobot.org/t/plr-dev-roadmap-2025-q1-q2/143) — extending to robotic arms (directly relevant)

## Known Hardware Issues

- **Gripper screw loosening** (motor 5) — apply Loctite 242/243 before long runs
- **USB disconnect during teleoperation** ([lerobot #3131](https://github.com/huggingface/lerobot/issues/3131)) — implement reconnect watchdog
- **Pipetting motion** should be decomposed into discrete phases for training (approach, insert tip, aspirate, move, dispense, eject)
- **50+ episodes minimum** per task, deliberate slow motions, 80k+ training steps

## Academic Papers

**What we reuse from papers:**

- **AutoBio**: open-source eval harness at `autobio-bench/AutoBio` — validate our policies against standard bio-lab tasks
- **DexMimicGen**: NVIDIA data amplification — 20 real demos to 2000 synthetic for ACT training
- **ArticuBot**: pre-trained fridge/door policy — zero-shot transfer for UC2, skip real fridge demos
- **InterACT/MoE-ACT**: replace vanilla ACT with inter-arm attention for bimanual pipetting
- **Tool-as-Interface**: collect pipetting demos from human video instead of robot teleoperation
- **Echo**: open-source force-feedback teleoperation — improve demo quality for tip press-fit
- **RoboCopilot**: human-in-the-loop correction loop — lab tech intervenes, corrections become training data
- **AIDASLab bimanual fork**: drop-in dual SO-101 support

### ETH / EPFL Lab Automation

| Paper | Year | Institution | Key Finding |
|-------|------|-------------|-------------|
| [PHIL](https://www.nature.com/articles/s41467-022-30643-7) | 2022 | ETH Zurich (Dettinger et al.) | Open-source personal pipetting robot. MIT. Tip management, media exchange. **Repo: [CSDGroup/PHIL](https://github.com/CSDGroup/PHIL)** |
| [SIMO](https://doi.org/10.3389/frobt.2024.1462717) | 2025 | EPFL (Scamarcio et al.) | Bi-manual robot (ABB GoFa), vision + tactile, 1.2mm accuracy, 95%+ success. Sets accuracy benchmark. |

### General Lab Automation

| Paper | Year | Key Finding |
|-------|------|-------------|
| [RoboCulture](https://arxiv.org/abs/2505.14941) | 2025 | Complete robotics platform for bio experiments. Aspuru-Guzik group (Toronto). |
| [AutoBio](https://arxiv.org/abs/2505.14030) | 2025 | Simulation benchmark for bio-lab tasks. Open-source eval harness. |
| [MatteriX](https://arxiv.org/abs/2601.13232) | 2026 | Digital twin for chemistry lab. Sim-to-real for pipetting. |
| [Microplate Handling Accuracy](https://www.biorxiv.org/content/10.1101/2023.12.29.573685v1) | 2024 | Positioning tolerance for 96-well plate grasping. |
| [Open Liquid Handler](https://www.biorxiv.org/content/10.64898/2026.03.02.709168v1) | 2026 | Industry-grade open-source liquid handler. PyLabRobot-compatible. |
| [Keyframe-Guided Rewards](https://arxiv.org/abs/2603.00719) | 2026 | RL reward shaping for long-horizon lab tasks. |
| [BioMARS](https://arxiv.org/abs/2507.01485) | 2025 | Multi-agent robot system for autonomous bio experiments. |
| [Dual Demonstration](https://arxiv.org/abs/2506.11384) | 2025 | Teaches end-effector AND jig operations simultaneously. |
| [Cutting the Cord](https://arxiv.org/abs/2603.09051) | 2026 | GPU-accelerated bimanual mobile manipulation on LeRobot/XLeRobot. |

### Imitation Learning (ACT & Bimanual)

| Paper | Year | Key Finding |
|-------|------|-------------|
| [ALOHA/ACT](https://arxiv.org/abs/2304.13705) | 2023 | Our training framework. 50 demos/task, low-cost bimanual. |
| [LeRobot](https://arxiv.org/abs/2602.22818) | 2026 | Our stack's authoritative reference. ICLR 2026. |
| [ALOHA Unleashed](https://arxiv.org/abs/2410.13126) | 2024 | More data > bigger model. DeepMind validation of ACT ceiling. |
| [InterACT](https://arxiv.org/abs/2409.07914) | 2024 | Hierarchical attention for inter-arm dependencies. |
| [MoE-ACT](https://arxiv.org/abs/2603.15265) | 2026 | One multi-task model via MoE. 5+ tasks without per-task training. |
| [DexMimicGen](https://arxiv.org/abs/2410.24185) | 2024 | 20 demos to 2000 synthetic. NVIDIA open-source. |
| [X-IL](https://arxiv.org/abs/2502.12330) | 2025 | Systematic policy architecture comparison. |
| [Bi-ACT](https://arxiv.org/abs/2401.17698) | 2024 | Bilateral force-feedback ACT. Contact-rich tasks. |
| [FTACT](https://arxiv.org/abs/2509.23112) | 2025 | Force-torque aware ACT. F/T sensor in observation space. |
| [Bimanual ACT](https://arxiv.org/abs/2503.13916) | 2025 | ACT + inter-arm coordination module. AIST Japan. |

### Tool Use & Door Opening

| Paper | Year | Key Finding |
|-------|------|-------------|
| [Tool-as-Interface](https://arxiv.org/abs/2504.04612) | 2025 | Learn from human tool-use video, not robot demos. |
| [FUNCTO](https://arxiv.org/abs/2502.11744) | 2025 | One-shot tool manipulation. Generalizes across variants. |
| [ArticuBot](https://arxiv.org/abs/2503.03045) | 2025 | Universal door/fridge policy. Zero-shot real transfer. |
| [UniDoorManip](https://arxiv.org/abs/2403.02604) | 2024 | Universal door policy (pull, push, sliding). |

### Data Collection

| Paper | Year | Key Finding |
|-------|------|-------------|
| [YOTO](https://arxiv.org/abs/2501.14208) | 2025 | One-shot bimanual from video. Near-zero demo cost. |
| [Echo](https://arxiv.org/abs/2504.07939) | 2025 | Force-feedback teleoperation. Open-source. |
| [RoboCopilot](https://arxiv.org/abs/2503.07771) | 2025 | Human-in-the-loop correction. Interventions become training data. |
| [GELLO](https://arxiv.org/abs/2309.13037) | 2023 | Low-cost replica-arm teleoperation (UC Berkeley). |
| [Taming VR Teleoperation](https://arxiv.org/abs/2508.14542) | 2025 | VR-based bimanual demo collection. Less operator fatigue. |
| [Opening Articulated Structures](https://arxiv.org/abs/2402.17767) | 2024 | Door/fridge opening without pre-mapped kinematics. |

## Cross-Cutting Insights

1. **Data > model complexity** — 50+ demos per task, amplify with DexMimicGen
2. **Force feedback is the main gap** — SO-101 has no wrist F/T sensor; biggest reliability risk for pipette tip press-fit
3. **Sim-to-real works for fridge/door** — ArticuBot demonstrates zero-shot transfer; may not need real demos for UC2
4. **Decompose pipetting into phases** — approach, insert tip, aspirate, dispense, eject. Train per-phase or use keyframe rewards
5. **Bimanual needs inter-arm attention** — vanilla ACT struggles with coupled coordination; use InterACT or MoE-ACT
6. **PyLabRobot backend driver** — writing one for SO-101 makes all existing protocols work on our arms ([#63](https://github.com/qte77/so101-biolab-automation/issues/63))
7. **8-channel pipette head** — 8x efficiency for 96-well work; design as a specialized end-effector
8. **Tool genesis is the frontier** — subsystems exist (LLM-to-CAD, auto-print, tool changing, VLM validation) but no one has closed the full loop yet (see [roadmap.md](roadmap.md#autonomous-tool-genesis-self-evolving-multi-tool))
