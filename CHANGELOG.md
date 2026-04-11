# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/), [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- E2E workflow orchestration (`app/so101/workflow.py`): UC1 pipetting (single/row/col/full plate), UC2 fridge ops, UC3 tool interchange, UC4 demo mode, UC5 gantry-based pipetting
- Multi-backend pipette architecture: `PipetteProtocol` interface with `DigitalPipette` (DIY) and `ElectronicPipette` (AELAB dPette 7016 / DLAB dPette+) backends
- `XZGantry` dedicated pipetting arm controller — 2-axis alternative to SO-101, supports Pololu Maestro + Pico W serial protocols
- `BentoLab` portable PCR thermocycler module — lid, programs, status
- Config-driven named positions in `configs/arms.yaml` with `move_to_named()`, `execute_sequence()`, `start_teleoperation()`
- Position sequence pipetting: `pipette_well` uses approach/lower patterns
- `PlateLayout` config loader and `create_workflow_context()` factory wiring all modules from YAML
- `--use-case` CLI dispatch in `run_demo.py`
- Dashboard: `run_workflow` WebSocket command, full component lifespan wiring
- `hardware/parts.json` manifest as single source of truth for all printable parts
- `hardware/render.py` unified runner — dispatches build123d or OpenSCAD per manifest
- Slicer validation script (`hardware/slicer/validate.py`) with graceful fallback when slicer unavailable
- STL mesh integrity check (`check_mesh_integrity`, `--structural` CLI flag)
- Position teaching (`teach_position`) and config persistence (`save_config`) for XZ gantry
- Makefile targets: `setup_cad`, `setup_scad`, `setup_slicer`, `render_parts`, `check_prints`, `render_all`

### Changed

- CAD backend migrated from CadQuery to build123d (Python 3.13 compatible, algebraic operators) — all 13 CAD files ported
- `app/` directory restructure: `src/biolab/` → `app/so101/`, `src/dashboard/` → `app/dashboard/`
- `hardware/cad/` reorganised into topic folders: `so101/`, `dpette/`, `labware/`, `deferred/`, `util/`
- `pipette_mount` redesigned for dPette barrel (ejector button cutout) — was digital-pipette-v2
- `tip_ejection_bar` redesigned from side-lever bar to top-button post to match dPette mechanism
- XZ gantry parts (`xz_gantry_frame`, `xz_carriage`) deferred — focus on SO-101 arm-held dPette
- Dashboard wired to real `DualArmController` + `SafetyMonitor` via FastAPI lifespan
- `workflow.py` now accepts `PipetteProtocol` instead of concrete `DigitalPipette`
- `camera.py`: cv2 import deferred to `start()` for headless environments
- Makefile: `.SILENT` / `.ONESHELL` / `.DEFAULT_GOAL`, `# MARK:` grouped help

### Fixed

- `arms.py`: stub-safe `get_observation` / `send_action` when LeRobot unavailable
- `pipette.py`: fill state tracking with over-aspiration / over-dispense guards

### Infrastructure

- Test suite: Hypothesis property tests (well coords, parse_well roundtrip, aspirate/dispense, joint limits)
- Quality gates: pytest coverage, pyright type checking, ruff lint (N/UP rules), cognitive complexity (max 15/function) via complexipy
- Docs: `docs/architecture.md`, `docs/UserStory.md`, `docs/demo-scenarios.md`, `docs/hardware/BOM.md`, `docs/notes.md`, `docs/roadmap.md`
- Documentation hierarchy declared in `CONTRIBUTING.md` with authority table; YAML frontmatter on all docs
- `.github/` infrastructure: issue templates, PR template, dependabot, CI workflows (ruff, pytest, CodeQL, link checker)
- `.devcontainer/devcontainer.json` for Codespace dev environment
- `.claude/` harness: settings, rules, statusline; plugins for python-dev, docs-governance, commit-helper, codebase-tools
- `LICENSE` (Apache-2.0)

## [0.1.0-alpha] — initial prototype

- SO-101 dual-arm controller + LeRobot integration (stub-safe)
- Workspace-frame coordinate commands, safety monitor watchdog
- FastAPI dashboard with WebSocket command channel
- OpenSCAD CAD pipeline for initial parts
