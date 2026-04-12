---
title: Roadmap & Future Vision
purpose: Forward-looking direction — closed-loop 3D printing, autonomous tool genesis, VLM/embodied AI phases
authority: Vision (INFORMATIONAL — not requirements)
created: 2026-03-27
updated: 2026-04-12
---

# Roadmap: Closed-Loop Automation & Autonomous Tool Genesis

Long-term direction for so101-biolab-automation. For actionable prior art and research, see [notes.md](notes.md).

## Overview

Toward general-purpose voice/agent-to-print. This repo is the first showcase.

**Human loop** — voice/text → LLM → build123d/OpenSCAD → slicer → print → human inspects → iterate

**Agent loop** — goal spec → agent generates CAD → slicer validates → printer API → camera + VLM inspects → agent fixes → reprints autonomously

**Milestones:**

1. **Done** — build123d + CuraEngine CLI pipeline (`make render_parts`, `make check_prints`)
2. **Done** — **PrusaLink API integration** as the first concrete printer API in the stack. MK4 slicer profiles (production PLA, prototype, TPU) + upload/print curl examples in [docs/hardware/prusa-mk4-ops.md](hardware/prusa-mk4-ops.md). Bambu remains the target for the agent-loop's camera+VLM step; PrusaLink fills the gap for single-printer workflows today.
3. **Done** — **Scan-informed parametric CAD**. First scan-derived parts delivered: `dpette_multi_handle` + `dpette_ejector_lever` from a 1:1 mm Revopoint scan of the DLAB dPette+ (see `hardware/scans/dpette/`). `parts.json` now carries a `scan_source` field for queryable scan provenance.
4. **Next** — LLM-assisted build123d generation from text prompts + scan input
5. **Future** — Autonomous agent loop with Bambu camera + VLM print inspection
6. **Vision** — Closed-loop tool genesis: agent identifies missing tool → generates CAD (optionally from a fresh scan) → slices → prints → mounts via tool changer → validates with VLM — true self-evolving multi-tool

## Closed-Loop 3D Printing

### Human Loop (voice/text → print)

```text
Human (voice/text) → LLM → OpenSCAD → STL → Slicer → Print
       ↑                                          |
       └── human inspects, describes fix ──────────┘
```

Human describes a part or modification in natural language (via CC `/voice` or text). LLM generates OpenSCAD, slicer validates, human inspects result and iterates.

### Agent Loop (goal → autonomous design-print-inspect)

```text
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

### Bambu camera + printer API (enables agent feedback)

- Built-in cameras: X1 (RTSP), A1/P1 (JPEG frames)
- Local MQTT: `<printer-ip>:8883`, topic `device/<serial>/report`
- Python: [`bambu-connect`](https://pypi.org/project/bambu-connect/), [`bambulabs-api`](https://pypi.org/project/bambulabs-api/)
- Cloud API: [`Bambu-Lab-Cloud-API`](https://github.com/coelacant1/Bambu-Lab-Cloud-API) (unofficial)

### Camera-based failure detection

| Tool | How | Printers |
|------|-----|----------|
| [Obico](https://github.com/TheSpaghettiDetective/obico-server) | Vision model, 30-60s intervals, auto-pause | OctoPrint, Klipper, Bambu |
| [OctoEverywhere Gadget](https://octoeverywhere.com/gadget) | Neural net trained on millions of prints | OctoPrint |
| [PrintWatch](https://plugins.octoprint.org/plugins/printwatch/) | AI video feed, auto-pause | OctoPrint |

### LLM/VLM agent loops for 3D printing

| Project | Architecture | Result |
|---------|-------------|--------|
| [LLM-3D Print](https://arxiv.org/abs/2408.14307) | Multi-agent: supervisor + VLM image reasoning + planner + executor → camera → corrects → reprints | 5x structural integrity, expert-level error ID |
| [Build Great AI](https://zenml.io/llmops-database/llm-powered-3d-model-generation-for-3d-printing) | Text → LLaMA/GPT/Claude → OpenSCAD → STL | Hours to minutes for design |
| [CADialogue](https://www.sciencedirect.com/science/article/abs/pii/S0010448525001678) | Multimodal LLM: text + speech + images → parametric CAD | Conversational CAD |

### Related projects (LLM + CAD/print)

| Project | What | Relation to us |
|---------|------|---------------|
| [ClaudeCAD](https://github.com/niklasmh/ClaudeCAD) | Claude + voice + web UI → STL download | Similar voice→CAD idea, web-only, no slicing or print control |
| [claude-3d-playground](https://github.com/ivanearisty/claude-3d-playground) | Claude Code for design, validate, slice | Closest competitor; no voice, no agent loop, no camera inspect |
| [openscad-agent](https://github.com/iancanderson/openscad-agent) | Claude Code agent for OpenSCAD modeling | Single-tool agent; no slicer, no print, no feedback loop |
| [CQAsk](https://github.com/OpenOrion/CQAsk) | LLM + CadQuery → STL/STEP with UI | Uses CadQuery not OpenSCAD; no print pipeline |
| [ScadLM](https://github.com/KrishKrosh/ScadLM) | Agentic AI + OpenSCAD generation | Early stage; no slicer validation or print control |
| [Text2CAD](https://github.com/SadilKhan/Text2CAD) | NeurIPS 2024: text → parametric CAD operations | Academic; 170K models dataset; no print integration |
| [text-2-cad](https://github.com/roberto-ceraolo/text-2-cad) | OpenAI + RAG over OpenSCAD docs → .scad | Early; similar LLM+OpenSCAD approach, minimal |
| [Speech-to-Reality](https://arxiv.org/html/2409.18390) | Voice → 3D generative AI → robotic assembly | See § "Autonomous Tool Genesis" for full analysis |

### MCP servers (integration layer)

| Server | What | Use for us |
|--------|------|-----------|
| [OctoEverywhere MCP](https://github.com/OctoEverywhere/mcp) | Printer control, camera, AI failure detection (OctoPrint/Klipper/Bambu) | Agent loop: send jobs, read camera, pause on failure |
| [OpenSCAD MCP](https://www.pulsemcp.com/servers/jhacksman-openscad) | Generate 3D models from text/images via OpenSCAD | Alternative to direct CLI; Claude Desktop integration |
| [CADQuery MCP](https://github.com/rishigundakaram/cadquery-mcp-server) | CAD generation + STL/STEP export + SVG feedback | CadQuery path if needed |

**Key insight:** No project integrates all layers (voice → design → validate → print → camera+VLM inspect → agent fix). The MCP ecosystem provides the building blocks.

## Autonomous Tool Genesis (Self-Evolving Multi-Tool)

**Vision:** Robot identifies missing tool → agent generates CAD → prints → mounts via tool changer → validates with VLM → iterates. No existing system fully closes this loop as of mid-2026.

### Tool Genesis Loop

```text
Task requires unknown tool
       ↓
Agent detects capability gap
       ↓
VLM/LLM designs tool (CadQuery/OpenSCAD)
       ↓
Slicer validates → Printer fabricates
       ↓
Robot mounts via tool changer
       ↓
Execute task → VLM validates result
       ↓ (fail)
Agent adjusts design → reprints
```

### Closest Existing Systems

| Project | Year | Institution | What | Gap vs Full Loop |
|---------|------|-------------|------|-----------------|
| [RobotSmith](https://arxiv.org/abs/2506.14763) | 2025 | UMass + MIT | VLM proposes tool geometry, simulates trajectories, 3D-prints, deploys on real robot. 50% success. NeurIPS 2025. | **Closest overall.** Fabrication handoff is manual, no iterative reprinting. |
| [VLMgineer](https://arxiv.org/abs/2507.12644) | 2025 | UPenn | VLMs co-design tool geometry + action plan via evolutionary search. 12-task benchmark. | Co-optimization of design+use. No physical fabrication in loop. |
| [Ringwald et al.](https://arxiv.org/abs/2210.10015) | 2022 | TU Munich | Two robots + two 3D printers. Auto print → mount → test gripper fingertips. Fully automated fab-to-deploy. | **Best physical pipeline.** Uses predefined STLs, no LLM design or gap detection. |
| [MAMA BEAR](https://www.bu.edu/articles/2024/a-robot-on-a-mission) | 2018+ | Boston U | Autonomous robot running 3+ years. Designs via Bayesian opt → prints → crush-tests → iterates. 25K+ structures. | **Gold standard for design-fabricate-test loop.** Structures, not tools. |
| [RoboTool](https://arxiv.org/abs/2310.13065) | 2023 | CMU + DeepMind | LLM reasons about when to **manufacture** a new tool vs select existing. Tested on real robots. | Demonstrated manufacturing reasoning. No actual CAD gen or printing. |

### Enabling Research

| Project | Year | Institution | What | Relevance |
|---------|------|-------------|------|-----------|
| [Learning to Design and Use Tools](https://arxiv.org/abs/2311.00754) | 2023 | Stanford / MIT | RL jointly learns designer policy (tool geometry) + controller policy (tool use). Zero-shot to unseen goals. CoRL 2023. | Joint design+control optimization — learns novel tool shapes. |
| [Speech to Reality](https://arxiv.org/abs/2409.18390) | 2025 | MIT CSAIL + DeepMind + Autodesk | Voice → LLM → 3D gen → robotic assembly. Builds furniture in ~5 min. ACM SCF '25 + NeurIPS. | Full prompt-to-physical-object loop (assembly, not printing). |
| [GAD (Generative AI + CAD)](https://link.springer.com/article/10.1007/s00170-025-15830-2) | 2025 | Springer | GPT-4o generates 3D models from text/images/voice → STL + G-code → direct to printer. | End-to-end text-to-print with printer integration. |
| [Generative AI for FreeCAD](https://arxiv.org/abs/2508.00843) | 2025 | Various | LLMs generate FreeCAD scripts from NL, iteratively refine on error feedback. | Directly applicable — parametric script gen for tool parts. |
| [CAD-LLM](https://www.research.autodesk.com/publications/ai-lab-cad-llm/) | 2024 | Autodesk Research | LLM generates parametric CAD from natural language. | Text-to-CAD backbone for fabrication pipeline. |
| [FiloBot](https://techxplore.com/news/2024-01-snake-robot-3d-body-longer.html) | 2024 | IIT Italy | Snake robot 3D-prints its own body to grow longer (FDM). Responds to stimuli. | Robot that literally fabricates itself — narrow but novel. |

### What's Missing (Open Problems)

No single system combines all six steps:

1. **Capability gap detection** — robot identifies it lacks a tool for a task
2. **LLM/VLM-driven CAD** — designs a novel tool parametrically
3. **Automated fabrication** — prints with quality monitoring ([LLM-3D Print](https://arxiv.org/abs/2408.14307))
4. **Robotic tool mounting** — picks up via quick-exchange (Ringwald has this)
5. **Task execution + validation** — uses tool, verifies success (RobotSmith has this)
6. **Iterative refinement** — redesigns and reprints on failure (MAMA BEAR has this for structures)

**Our position:** Steps 1-2-3 via build123d + PrusaSlicer + Bambu printer. Step 4 via SO-101 tool changer. Steps 5-6 via VLM camera loop. Assembling these subsystems into a unified pipeline is the frontier.

## VLM + Embodied AI for Hands-Off Autonomous Operation

### Operation Modes (Progressive)

```text
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

## Near-Term Actions (When Hardware Arrives)

1. Use [AIDASLab bimanual fork](https://github.com/AIDASLab/lerobot-so101-bimanual) for dual-arm setup
2. Apply Loctite 242 to motor 5 screws on all arms
3. Print [reinforced trigger](https://www.printables.com/model/1323562) for leader arm
4. Print [parallel gripper](https://makerworld.com/en/models/1549112) as pipette holder base
5. Port Berkeley tool changer cone to SO-101 wrist dimensions
6. Record 50 episodes per task using decomposed motion phases
7. Train ACT via LeRobot; evaluate on AutoBio benchmark
8. Implement USB watchdog for long-run stability
