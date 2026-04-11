---
title: Architecture
purpose: System design, module responsibilities, data flows, stub mode, design decisions
authority: System design (AUTHORITY)
created: 2026-03-27
updated: 2026-04-10
---

# Architecture

## System Overview

```text
┌──────────────────────────────────────────────────────┐
│                  Remote Dashboard                     │
│  FastAPI + WebSocket commands + REST /api/status      │
│  app/dashboard/server.py                              │
└──────────────────┬───────────────────────────────────┘
                   │ WebSocket: e_stop, heartbeat,
                   │ target_well, run_workflow
┌──────────────────▼───────────────────────────────────┐
│               Workflow Orchestration                  │
│  app/so101/workflow.py                               │
│  Composes modules into use cases (UC1-4)              │
│  Loads PlateLayout from configs/plate_layout.yaml     │
├──────────┬──────────┬──────────┬─────────────────────┤
│  Arms    │ Pipette  │  Tool    │  Safety             │
│  Control │ Control  │  Changer │  Monitor            │
│ arms.py  │pipette.py│tool_ch.. │ safety.py           │
└────┬─────┴────┬─────┴────┬─────┴─────────────────────┘
     │          │          │
     │     ┌────▼────┐     │
     │     │ Plate   │     │
     │     │ Geometry │     │
     │     │plate.py │     │
     │     └─────────┘     │
     │                     │
┌────▼─────────────────────▼───┐
│  LeRobot / Serial / Hardware │
│  (stub mode when unavailable)│
└──────────────────────────────┘
```

## Module Responsibilities

| Module | File | Responsibility | Dependencies |
|--------|------|----------------|--------------|
| **Workflow** | `app/so101/workflow.py` | Orchestrates use cases (UC1-5) by composing other modules | arms, pipette, plate, tool_changer, xz_gantry |
| **Arms** | `app/so101/arms.py` | Dual SO-101 arm control via LeRobot. Config-driven named positions, sequences, teleoperation skeleton. Stub mode when lerobot absent. | plate (for send_to_well) |
| **Pipette** | `app/so101/pipette.py` | Multi-backend pipette control (`PipetteProtocol`). Backends: `DigitalPipette` (DIY/Arduino), `ElectronicPipette` (AELAB/DLAB). Stub mode when pyserial absent. | None |
| **XZ Gantry** | `app/so101/xz_gantry.py` | Dedicated 2-axis pipetting arm (simpler than SO-101). Stub mode when serial absent. | None |
| **Bento Lab** | `app/so101/bento_lab.py` | Portable PCR thermocycler control (lid, programs, status). Stub mode when serial absent. | None |
| **Plate** | `app/so101/plate.py` | Pure SBS 96-well coordinate math. No hardware deps. | None |
| **Tool Changer** | `app/so101/tool_changer.py` | 3-tool magnetic dock: pipette, gripper, fridge hook. | arms (for send_action) |
| **Camera** | `app/so101/camera.py` | Multi-camera capture via OpenCV. Stub mode when cv2 absent. | None |
| **Safety** | `app/so101/safety.py` | Watchdog, e-stop, joint limits. Pure Python. | None |
| **Dashboard** | `app/dashboard/server.py` | FastAPI server with WebSocket commands and REST status. | All biolab modules |

## Data Flow: Pipetting a Well

```text
User/Dashboard → workflow.pipette_well()
  1. arm.execute_sequence("arm_a", ["trough_approach", "trough_lower"])  → arms.py → LeRobot
  2. pipette.aspirate(50.0)                → pipette.py → Arduino serial (stub: track fill)
  3. arm.execute_sequence("arm_a", ["well_approach", "well_lower"])      → arms.py → LeRobot
  4. pipette.dispense(50.0)                → pipette.py → Arduino serial (stub: track fill)
```

## Data Flow: Tool Change

```text
workflow.uc2_fridge_open_grab_move()
  1. changer.change_tool(FRIDGE_HOOK)      → tool_changer.py → arms.send_action (dock sequence)
  2. arm.send_action(FRIDGE_APPROACH)       → arms.py → LeRobot
  3. arm.send_action(FRIDGE_HOOK_ENGAGED)   → arms.py → LeRobot
  4. changer.change_tool(GRIPPER)           → tool_changer.py → arms.send_action (dock sequence)
  5. arm.send_action(FRIDGE_GRAB)           → arms.py → LeRobot
```

## Configuration Files

| File | Loaded By | Content |
|------|-----------|---------|
| `configs/arms.yaml` | `DualArmConfig.from_yaml()` | Arm ports, cameras, named positions (park, home, well_approach, etc.) |
| `configs/plate_layout.yaml` | `PlateLayout.from_yaml()` | Workspace origin, Z heights, trough position |
| `configs/tool_dock.yaml` | `ToolDockConfig.from_yaml()` | Joint arrays for 3 dock stations |
| `configs/pipette.yaml` | `_create_pipette()` | Backend selection (digital/electronic) + per-backend settings |
| `configs/xz_gantry.yaml` | `XZGantryConfig.from_yaml()` | Named positions, serial port, controller type |
| `configs/bento_lab.yaml` | `BentoLabConfig` | Serial port, PCR program definitions |

## Stub Mode

Every hardware-dependent module gracefully degrades when its dependency is unavailable:

| Module | Trigger | Behavior |
|--------|---------|----------|
| arms.py | `ImportError` on `lerobot` | `send_action` logs and returns; `get_observation` returns `{"stub": True}` |
| pipette.py | `ImportError` on `serial` | Fill state tracked in memory; serial commands are no-ops |
| xz_gantry.py | `ImportError` on `serial` | Position tracked in memory; serial commands are no-ops |
| bento_lab.py | `ImportError` on `serial` | State (lid, program) tracked in memory; serial commands are no-ops |
| camera.py | `ImportError` on `cv2` | `start()` returns; `get_frames()` returns `{}` |

This allows the full workflow to run end-to-end without any hardware attached. Run `make run_tests` to verify.

## Key Design Decisions

- **No IK**: `send_to_well()` uses config `well_approach` position; real inverse kinematics deferred to MVP (requires calibrated hardware). Named positions in `configs/arms.yaml` are placeholders.
- **PlateLayout in workflow.py**: Separates pure SBS math (plate.py) from hardware workspace config (workflow.py). Single responsibility.
- **No fridge module**: Fridge joint arrays are constants in workflow.py. YAGNI until hardware exists.
- **Dashboard runs workflow in thread**: `run_workflow` WebSocket command spawns `uc4_demo_all` in a daemon thread to avoid blocking the event loop.

## Prior Art & Vision

- [docs/notes.md](notes.md) — academic papers, community designs, tools, known hardware issues informing these decisions
- [docs/roadmap.md](roadmap.md) — forward-looking direction (closed-loop printing, tool genesis, VLM/embodied AI phases)
