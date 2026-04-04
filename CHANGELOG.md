# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/), [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- E2E workflow orchestration (`src/biolab/workflow.py`): UC1 pipetting (single/row/col/full plate), UC2 fridge ops, UC3 tool interchange, UC4 demo mode
- `PlateLayout` config loader for workspace-frame coordinates
- `create_workflow_context()` factory wiring all modules from YAML
- `--use-case` CLI dispatch in `run_demo.py`
- Dashboard: `run_workflow` WebSocket command, full component lifespan wiring
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

### Changed

- Dashboard wired to real `DualArmController` + `SafetyMonitor` via FastAPI lifespan
- `camera.py`: cv2 import deferred to `start()` for headless environments
- `arms.py`: stub-safe `get_observation`/`send_action`, added `send_to_well()` + `park_all()`
- `pipette.py`: fill state tracking with over-aspiration/over-dispense guards
- Makefile: `.SILENT`/`.ONESHELL`, `.DEFAULT_GOAL`, `# MARK:` grouped help, removed `render_parts`/`setup_cad`
- SVGs generated as isometric wireframes (CadQuery) or 2D projections (OpenSCAD fallback) with dark mode theming
- `render_scad` renamed to `render_parts` with CadQuery/OpenSCAD fallback logic
- `check_prints` now delegates slicer detection to `validate.py` (no Makefile binary check)
- `pyproject.toml`: dependency-groups, pytest ini_options, ruff N/UP, pyright
