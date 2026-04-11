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

See [docs/UserStory.md](docs/UserStory.md) for use cases (UC1-5) and acceptance criteria.

## Hardware

**SO-101 path:** Two [SO-101](https://github.com/therobotstudio/so-arm100) follower arms + one leader arm via [LeRobot](https://huggingface.co/docs/lerobot/index). ~$350–$650.

**XZ gantry path:** Dedicated 2-axis pipetting arm (MGN12 rails + NEMA17 steppers). ~$60–$80.

See [docs/hardware/BOM.md](docs/hardware/BOM.md) for full shopping list with links.

## Quick Start

```bash
# Setup (all deps + tools)
make setup_all

# Generate 3D-printed parts (build123d preferred, OpenSCAD fallback)
make render_parts

# Optional: validate printability (CuraEngine / PrusaSlicer)
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

- `app/` — software (arms, pipette, workflow, dashboard, CAD pipeline)
- `hardware/` — CAD sources, STLs, SVGs for 3D-printed parts
- `configs/` — YAML runtime config (ports, positions, backends)
- `scripts/` — CLI entry points
- `docs/` — design, user stories, demo scenarios, BOM, research
- `tests/` — unit + property tests

See [docs/architecture.md](docs/architecture.md) for module responsibilities and data flows.

## Documentation

- [Architecture](docs/architecture.md) — system design, module responsibilities, data flows
- [User Stories](docs/UserStory.md) — use case (UC1-5) acceptance criteria
- [Demo Scenarios](docs/demo-scenarios.md) — how to run and verify each use case
- [Hardware BOM](docs/hardware/BOM.md) — shopping list with links ($350-$3000+)
- [Research Notes](docs/notes.md) — prior art, papers, tools, known issues
- [Roadmap](docs/roadmap.md) — closed-loop printing, tool genesis, VLM/embodied AI vision

## Key Dependencies

- [LeRobot](https://github.com/huggingface/lerobot) — Teleoperation + imitation learning
- [PyLabRobot](https://github.com/PyLabRobot/pylabrobot) — Liquid handling abstractions
- [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2) — DIY pipette (alternative backend)
- [build123d](https://github.com/gumyr/build123d) — Primary CAD for 3D-printed parts
- [OpenSCAD](https://openscad.org/) — Fallback CAD for 3D-printed parts
- [CuraEngine](https://github.com/Ultimaker/CuraEngine) — Printability validation (headless, preferred)
- [PrusaSlicer](https://github.com/prusa3d/PrusaSlicer) — Printability validation (fallback)
- FastAPI + WebRTC — Remote dashboard
- OpenCV — Camera pipeline

## Development

For dev setup, testing, and contribution workflow, see [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).
Run `make help` to list available targets; `make validate` is the canonical quality gate.

## Roadmap

Toward general-purpose voice/agent-to-print. See [docs/roadmap.md](docs/roadmap.md) for full vision (human loop, agent loop, autonomous tool genesis, VLM/embodied AI phases).

## License

Apache-2.0
