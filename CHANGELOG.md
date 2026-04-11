# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/), [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Prusa MK4 slicer profiles** (4 new `.ini` files under `app/hardware/slicer/profiles/`): `prusa_mk4_pla_02mm` (production PLA/PLA+), `prusa_mk4_pla_prototype` (fast 0.3mm fit-check), `prusa_mk4_pla_prototype_supports` (with auto-supports), `prusa_mk4_tpu_02mm` (TPU 95A)
- **PrusaLink API operations reference** (`docs/hardware/prusa-mk4-ops.md`): endpoint catalog, digest auth, upload + print-after-upload curl examples, CAD-to-print pipeline
- **dPette+ 3D scan reference data**: `hardware/scans/dpette/0410_02_mesh.{ply,stl}` (1:1 mm Revopoint scan) + `hardware/scans/dpette/README.md` (provenance, scale, intended use)
- **5 new dPette CAD parts** (build123d, ported from Antonio Lamb's PR #48 CadQuery source): `dpette_handle` (U-bracket single-channel mount), `dpette_cam_arm` (M6 horn radial arm), `dpette_tip_release` (L-bracket ejector station), `dpette_multi_handle` (Ø32mm split-bore clamp — scan-derived, replaces SO-101 bottom jaw), `dpette_ejector_lever` (M6-horn lever, replaces SO-101 top jaw, ~175N)
- **`diagramforge` submodule** (<https://github.com/qte77/diagramforge>) for interactive SVG/drawio design with Claude Code and other agents
- `scan_source` optional field in `app/hardware/parts.json` for scan-derived parts — queryable provenance pointing at `hardware/scans/` inputs
- `Hardware Asset Layout` section in `docs/architecture.md` describing the code/assets split and scan data as optional CAD input
- `ASSETS_DIR` constant in `tests/_paths.py` for the new top-level `hardware/` path
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

- **Code / assets split**: generated STL + SVG outputs moved from `app/hardware/{stl,svg}/` to top-level `hardware/{stl,svg}/`. Code (CAD scripts, `render.py`, `slicer/`, `parts.json`) stays under `app/hardware/`. New top-level `hardware/scans/` for reference 3D scan data. `render.py`, `slicer/validate.py`, `cad/util/export.py`, `tests/_paths.py` all updated to resolve asset paths via a new `ASSETS_DIR` anchor.
- `app/hardware/README.md` restructured: removed duplicated Parts Table (→ points at `parts.json` as single source of truth + `jq` query examples) and duplicated layout description (→ points at `docs/architecture.md`). Added dPette+ 8-ch Mount + dPette single-channel Mount + Scan Reference Data assembly sections, Prusa MK4 slicer profile catalog.
- `parts.json` `notes` fields trimmed to short descriptive labels — provenance prose moved to commit history per DRY.
- `README.md` (root): Workspace Layout image link updated to `hardware/svg/system_overview.svg`
- `dpette_cam_arm` tip geometry: `Sphere` → `Cylinder` (functionally equivalent; Sphere+Cylinder composites broke build123d's 2D SVG projection)
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

- `app/hardware/cad/util/export.py` (`export_part`): handles `ShapeList` results from build123d boolean operations via a `_to_compound` coercion helper (disconnected shapes no longer fail with `AttributeError: ShapeList has no wrapped`)
- `tests/so101/test_arms.py`: pre-existing ruff drift — B007 (unused loop var `arm_id` → `_arm_id`) + RUF043 (non-raw regex `"[Ll]eader"` → `r"[Ll]eader"` in `pytest.raises(match=...)`)
- `arms.py`: stub-safe `get_observation` / `send_action` when LeRobot unavailable
- `pipette.py`: fill state tracking with over-aspiration / over-dispense guards

### Infrastructure

- `tests/hardware/test_scad_svg.py`: resolves SVG paths via `ASSETS_DIR` (top-level `hardware/svg/`) instead of `HARDWARE_DIR` (`app/hardware/svg/`) — follows the code/assets split
- `AGENT_LEARNINGS.md` entries: `make test` excludes hardware/network tests by default via `pyproject.toml:79` `addopts`; git log direction hazard — always use explicit `A..B` ranges instead of one-sided `git log B -N`
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
