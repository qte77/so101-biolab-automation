# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/), [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- E2E workflow orchestration (`src/biolab/workflow.py`): UC1 pipetting (single/row/col/full plate), UC2 fridge ops, UC3 tool interchange, UC4 demo mode
- `PlateLayout` config loader for workspace-frame coordinates
- `create_workflow_context()` factory wiring all modules from YAML
- `--use-case` CLI dispatch in `run_demo.py`
- Dashboard: `run_workflow` WebSocket command, full component lifespan wiring
- `hardware/parts.json` manifest as single source of truth for all 10 printable parts
- `hardware/render.py` unified runner — reads manifest, dispatches CadQuery or OpenSCAD
- CadQuery scripts (`hardware/cad/`) as primary STL+SVG generator, OpenSCAD (`hardware/scad/`) as runtime fallback
- PrusaSlicer validation script (`hardware/slicer/validate.py`) with graceful fallback when slicer unavailable
- Makefile targets: `setup_cad`, `setup_scad`, `setup_slicer`, `render_parts`, `check_prints`, `render_all`
- Generated STL + SVG: plate holder, tool changer cones, fridge hook
- `docs/architecture.md`, `docs/UserStory.md`, `docs/demo-scenarios.md`
- `docs/hardware/BOM.md` with first-party sourced links
- `docs/research.md` — community designs, papers, future vision
- YAML frontmatter on all docs (title, purpose, authority, dates)
- Documentation hierarchy in `CONTRIBUTING.md` with authority table
- `.github/` infrastructure: issue templates, PR template, dependabot, CI workflows
- `.devcontainer/devcontainer.json` for Codespace dev environment
- `.claude/` harness: settings.json, rules (core-principles, context-management, compound-learning, robotics-safety, testing), statusline
- CC plugins: python-dev, docs-governance, commit-helper, codebase-tools
- `LICENSE` (Apache-2.0)
- 104 tests across 11 test files
- `PipetteProtocol` interface + `ElectronicPipette` backend for AELAB dPette 7016 / DLAB dPette+ (`src/biolab/pipette.py`)
- `XZGantry` dedicated pipetting arm controller (`src/biolab/xz_gantry.py`) — simpler 2-axis alternative to SO-101
- `BentoLab` portable PCR thermocycler module (`src/biolab/bento_lab.py`) — lid, programs, status
- YAML configs: `configs/pipette.yaml`, `configs/xz_gantry.yaml`, `configs/bento_lab.yaml`
- USB RE tools, commercial pipettes, Bento Lab, XZ gantry in `docs/research.md` and `docs/hardware/BOM.md`
- UC5 gantry-based pipetting workflow (`uc5_gantry_pipette`, `uc5_gantry_strip`) — XZ gantry + any PipetteProtocol backend
- `status`, `notes`, `primary_backend` fields in `hardware/parts.json` manifest
- Pololu Maestro + Pico W serial protocols in XZ gantry (`xz_gantry.py`)
- Position teaching (`teach_position`) and config persistence (`save_config`) for XZ gantry
- STL mesh integrity check (`check_mesh_integrity` in `validate.py`, `--structural` CLI flag)
- Structural review checklist in `hardware/stl/README.md`
- 4 planned XZ gantry parts in manifest (frame, carriage, dPette cradles)
- OpenSCAD scripts marked as archived fallback (`hardware/scad/README.md`)
- Reorganized `hardware/cad/` into topic folders: `so101/`, `dpette/`, `labware/`, `deferred/`, `util/`
- Redesigned `pipette_mount` for dPette barrel (ejector button cutout) — was digital-pipette-v2
- Redesigned `tip_ejection_bar` from side-lever bar to top-button post (matches dPette mechanism)
- `render.py` skips deferred/planned parts automatically
- XZ gantry parts (`xz_gantry_frame`, `xz_carriage`) deferred — focus on SO-101 arm-held dPette
- 167 tests across 16 test files

### Changed

- Dashboard wired to real `DualArmController` + `SafetyMonitor` via FastAPI lifespan
- `camera.py`: cv2 import deferred to `start()` for headless environments
- `arms.py`: stub-safe `get_observation`/`send_action`, added `send_to_well()` + `park_all()`
- `pipette.py`: fill state tracking with over-aspiration/over-dispense guards; multi-backend via `PipetteProtocol`
- `workflow.py`: accepts `PipetteProtocol` instead of concrete `DigitalPipette`; `_create_pipette()` factory reads `configs/pipette.yaml`
- `hardware/render.py`: respects per-part `primary_backend` field from manifest
- `hardware/parts.json`: parts audited — 7 active, 1 redesign (pipette_mount), 2 deferred (fridge_hook, tool_cone_hook)
- Makefile: `.SILENT`/`.ONESHELL`, `.DEFAULT_GOAL`, `# MARK:` grouped help, removed `render_parts`/`setup_cad`
- SVGs generated as isometric wireframes (CadQuery) or 2D projections (OpenSCAD fallback) with dark mode theming
- `render_scad` renamed to `render_parts` with CadQuery/OpenSCAD fallback logic
- `check_prints` now delegates slicer detection to `validate.py` (no Makefile binary check)
- `pyproject.toml`: dependency-groups, pytest ini_options, ruff N/UP, pyright
