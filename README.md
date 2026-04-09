# so101-biolab-automation

> **PROTOTYPE** — This project is in early development. Hardware designs are untested, CAD dimensions are approximate, and USB protocols are being reverse-engineered. Not ready for production use. Contributions and feedback welcome.

[![License](https://img.shields.io/badge/license-Apache2.0-58f4c2.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.1.0--alpha-58f4c2.svg)
[![CodeQL](https://github.com/qte77/so101-biolab-automation/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/so101-biolab-automation/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/so101-biolab-automation/badge)](https://www.codefactor.io/repository/github/qte77/so101-biolab-automation)
[![ruff](https://github.com/qte77/so101-biolab-automation/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/so101-biolab-automation/actions/workflows/ruff.yaml)
[![pytest](https://github.com/qte77/so101-biolab-automation/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/so101-biolab-automation/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/qte77/so101-biolab-automation/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/qte77/so101-biolab-automation/actions/workflows/links-fail-fast.yaml)

[![Flat Repo (UitHub)](https://img.shields.io/badge/Flat_Repo-uithub-800080.svg)](https://uithub.com/qte77/so101-biolab-automation)
[![Flat Repo (GitToDoc)](https://img.shields.io/badge/Flat_Repo-GitToDoc-fe4a60.svg)](https://gittodoc.com/qte77/so101-biolab-automation)
[![vscode.dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=vscode.dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://vscode.dev/github/qte77/so101-biolab-automation)
[![Codespace Dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/so101-biolab-automation)

Dual-path bio-lab automation: SO-101 arms for complex tasks + XZ gantry for dedicated pipetting. Supports commercial electronic pipettes (AELAB dPette, DLAB dPette+) and Bento Lab PCR.

## What This Demonstrates

- **Dual-path architecture** — SO-101 6-DOF arms for tool changing and fridge ops; XZ gantry for dedicated pipetting
- **Multi-backend pipettes** — PipetteProtocol supports DIY (digital-pipette-v2) and commercial (AELAB/DLAB) backends
- **Teacher-student learning** — Leader arm teaches follower via imitation learning (ACT policy)
- **Remote oversight** — WebSocket command injection + dashboard from browser
- **Tool changing** — Arms swap between pipette, gripper, and fridge hook autonomously
- **PCR integration** — Bento Lab thermocycler module (stub, control interface TBD)

## Hardware

**SO-101 path:** Two [SO-101](https://github.com/therobotstudio/so-arm100) follower arms + one leader arm via [LeRobot](https://huggingface.co/docs/lerobot/index). ~$350–$650.

**XZ gantry path:** Dedicated 2-axis pipetting arm (MGN12 rails + NEMA17 steppers). ~$60–$80.

See [docs/hardware/BOM.md](docs/hardware/BOM.md) for full shopping list with links.

## Quick Start

```bash
# Setup (all deps + tools)
make setup_all

# Generate 3D-printed parts (CadQuery preferred, OpenSCAD fallback)
make render_parts

# Optional: validate printability (PrusaSlicer)
make setup_slicer
make check_prints

# Calibrate arms
make calibrate_arms

# Teleoperate (teacher-student)
make start_teleop

# Record pipetting episodes
make record_episodes TASK="pipette row A"

# Train policy
make train_policy

# Run demo
make run_demo
```

## Architecture

![Workspace Layout](hardware/svg/system_overview.svg)

See [docs/architecture.md](docs/architecture.md) for full system design, module responsibilities, and data flows.

## Project Structure

```text
src/biolab/        Core: arms, pipette (multi-backend), xz_gantry, bento_lab, plate, tool changer, safety, workflow
src/dashboard/     FastAPI server, WebSocket commands, browser UI
scripts/           CLI entry points for use cases and demo orchestration
configs/           Arm ports, plate layout, tool dock, pipette backend, XZ gantry, Bento Lab (YAML)
hardware/cad/      CadQuery scripts — primary STL+SVG generation
hardware/scad/     OpenSCAD scripts — fallback STL generation
hardware/slicer/   PrusaSlicer CLI printability validation (optional)
hardware/stl/      Generated STL files (via make render_parts, gitignored)
hardware/svg/      SVG 2D projections of parts (tracked, for documentation)
docs/              Architecture, user stories, demo scenarios, BOM, research
tests/             165 tests across 16 test files
```

## Documentation

- [Architecture](docs/architecture.md) — system design, module responsibilities, data flows
- [User Stories](docs/UserStory.md) — use case (UC1-5) acceptance criteria
- [Demo Scenarios](docs/demo-scenarios.md) — how to run and verify each use case
- [Hardware BOM](docs/hardware/BOM.md) — shopping list with links ($350-$3000+)
- [Research](docs/research.md) — community designs, papers, future vision (VLM, embodied AI)

## Key Dependencies

- [LeRobot](https://github.com/huggingface/lerobot) — Teleoperation + imitation learning
- [PyLabRobot](https://github.com/PyLabRobot/pylabrobot) — Liquid handling abstractions
- [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2) — DIY pipette (alternative backend)
- [CadQuery](https://github.com/CadQuery/cadquery) — Primary CAD for 3D-printed parts
- [OpenSCAD](https://openscad.org/) — Fallback CAD for 3D-printed parts
- [PrusaSlicer](https://github.com/prusa3d/PrusaSlicer) — Printability validation (optional)
- FastAPI + WebRTC — Remote dashboard
- OpenCV — Camera pipeline

## Roadmap

Toward general-purpose voice/agent-to-print. This repo is the first showcase.

**Human loop** — voice/text → LLM → OpenSCAD → slicer → print → human inspects → iterate

**Agent loop** — goal spec → agent generates CAD → slicer validates → printer API → camera + VLM inspects → agent fixes → reprints autonomously

1. **Done** — CadQuery + PrusaSlicer CLI pipeline (`make render_parts`, `make check_prints`)
2. **Next** — LLM-assisted CadQuery generation from text prompts
3. **Future** — Autonomous agent loop with Bambu camera + VLM print inspection
4. **Vision** — Closed-loop tool genesis: agent identifies missing tool → generates CadQuery → slices → prints → mounts via tool changer → validates with VLM — true self-evolving multi-tool

See [docs/research.md](docs/research.md) § "Closed-Loop 3D Printing" for prior art.

## License

Apache-2.0
