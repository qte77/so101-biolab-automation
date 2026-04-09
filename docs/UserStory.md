---
title: User Stories
purpose: Acceptance criteria for use cases UC1-5 (pipetting, fridge, tool change, remote oversight, gantry) + developer stories
authority: Acceptance criteria (AUTHORITY)
created: 2026-03-27
updated: 2026-03-27
---

# User Stories & Acceptance Criteria

Each use case (UC) groups one or more user stories (US) with acceptance criteria.

## Roles

- **Lab researcher** — operates the system to automate pipetting and sample handling
- **Remote operator** — monitors and controls the system via web dashboard
- **Developer** — extends the system with new workflows and hardware support

## Pipetting (UC1)

### US-1.1: Single Well Pipetting

> As a **lab researcher**, I want to pipette a specific volume from the reagent trough to a single well, so that I can prepare individual samples.

**Acceptance criteria:**

- [ ] Specify target well by name (e.g., A1, H12) and volume in µL
- [ ] Arm moves to trough, aspirates, moves to well, dispenses
- [ ] Pipette fill returns to 0 after dispense
- [ ] Invalid well name raises clear error

**Command:** `python scripts/run_demo.py --use-case uc1_single --well A1 --volume 50`

### US-1.2: Row/Column Pipetting

> As a **lab researcher**, I want to pipette an entire row or column in one command, so that I can prepare a set of samples without repeating commands.

**Acceptance criteria:**

- [ ] Specify row (A-H) or column (1-12) and volume per well
- [ ] All wells in the row/column receive the specified volume
- [ ] Each well gets an independent aspirate→dispense cycle
- [ ] Invalid row/column raises clear error

**Commands:**

- `python scripts/run_demo.py --use-case uc1_row --row A --volume 25`
- `python scripts/run_demo.py --use-case uc1_col --col 1 --volume 20`

### US-1.3: Full Plate Pipetting

> As a **lab researcher**, I want to pipette all 96 wells of a plate in one command, so that I can prepare a full experiment plate hands-free.

**Acceptance criteria:**

- [ ] All 96 wells (A1 through H12) receive the specified volume
- [ ] Pipette never overflows (each well is an independent aspirate→dispense)
- [ ] Sequence follows row-major order (A1, A2, ..., H12)

**Command:** `python scripts/run_demo.py --use-case uc1_full --volume 20`

## Fridge Operations (UC2)

### US-2.1: Retrieve Item from Fridge

> As a **lab researcher**, I want the arm to open a fridge, grab a reagent plate, and move it to the workspace, so that I can access cold-stored samples without manual intervention.

**Acceptance criteria:**

- [ ] Arm equips fridge hook tool
- [ ] Hook engages fridge door handle, pulls open
- [ ] Arm swaps to gripper tool
- [ ] Gripper grabs item from fridge shelf
- [ ] Arm moves item to park (safe workspace) position

**Command:** `python scripts/run_demo.py --use-case uc2`

## Tool Interchange (UC3)

### US-3.1: Swap Tools Autonomously

> As a **lab researcher**, I want the arm to change its end-effector without manual intervention, so that it can switch between pipetting and sample transport tasks.

**Acceptance criteria:**

- [ ] Arm returns current tool to magnetic dock station
- [ ] Arm picks up target tool from dock
- [ ] Supports 3 tools: pipette, gripper, fridge hook
- [ ] Changing to the already-equipped tool is a no-op

**Command:** `python scripts/run_demo.py --use-case uc3`

## Remote Oversight (UC4)

### US-4.1: Monitor and Control via Dashboard

> As a **remote operator**, I want to view system status and send commands from a web browser, so that I can oversee and intervene in lab operations from anywhere.

**Acceptance criteria:**

- [ ] Dashboard accessible at `http://localhost:8080`
- [ ] Live status: mode, e-stop state, arm connection, arm IDs
- [ ] Commands via WebSocket: e-stop, heartbeat, pause, resume, target well, run workflow
- [ ] E-stop triggers SafetyMonitor and parks all arms
- [ ] Heartbeat resets watchdog timer (5s timeout → auto-park)

**Command:** `make serve_dashboard`

### US-4.2: Run Full Demo Remotely

> As a **remote operator**, I want to trigger the full demo sequence from the dashboard, so that I can demonstrate all capabilities without CLI access.

**Acceptance criteria:**

- [ ] "Run Demo" button in dashboard triggers UC4 (all use cases)
- [ ] Workflow runs in background (dashboard stays responsive)
- [ ] Status endpoint reflects "running" mode during execution

## Gantry Pipetting (UC5)

### US-5.0: Gantry-Based Pipetting

> As a **lab researcher**, I want to pipette using the simpler XZ gantry instead of the SO-101 arm, so that I can run repetitive pipetting at fixed positions with minimal setup.

**Acceptance criteria:**

- [ ] Gantry moves to source position, lowers, pipette aspirates, raises
- [ ] Gantry moves to destination position, lowers, pipette dispenses, raises
- [ ] Works with any PipetteProtocol backend (DigitalPipette or ElectronicPipette)
- [ ] Strip mode pipettes multiple destinations from a single source
- [ ] Invalid position name raises clear error

**Commands:**

- `python scripts/run_demo.py --use-case uc5_gantry --volume 50`

## Developer Stories

### US-5.1: Extend with New Workflow

> As a **developer**, I want to add a new use case by composing existing modules, so that I can automate new lab tasks without modifying core modules.

**Acceptance criteria:**

- [ ] New workflow composes existing modules via `create_workflow_context()`
- [ ] No modifications to core modules (`arms.py`, `pipette.py`, `plate.py`, etc.)
- [ ] New workflow has corresponding tests in `tests/`

See [docs/architecture.md](architecture.md) for module API and composition patterns.

### US-5.2: Run All Tests Without Hardware

> As a **developer**, I want all tests to pass without physical hardware attached, so that I can develop and CI/CD in any environment.

**Acceptance criteria:**

- [ ] `uv run pytest` passes on any machine with Python 3.10+
- [ ] No `@pytest.mark.hardware` tests run by default
- [ ] Stub mode automatically activates when lerobot/pyserial/cv2 unavailable

**Command:** `make validate`
