# Architecture

## System Overview

```
┌──────────────────────────────────────────────────────┐
│                  Remote Dashboard                     │
│  FastAPI + WebSocket commands + REST /api/status      │
│  src/dashboard/server.py                              │
└──────────────────┬───────────────────────────────────┘
                   │ WebSocket: e_stop, heartbeat,
                   │ target_well, run_workflow
┌──────────────────▼───────────────────────────────────┐
│               Workflow Orchestration                  │
│  src/biolab/workflow.py                               │
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
| **Workflow** | `src/biolab/workflow.py` | Orchestrates UC1-4 by composing other modules | arms, pipette, plate, tool_changer |
| **Arms** | `src/biolab/arms.py` | Dual SO-101 arm control via LeRobot. Stub mode when lerobot absent. | plate (for send_to_well), safety (for PARK_POSITION) |
| **Pipette** | `src/biolab/pipette.py` | Digital pipette serial control. Tracks fill state. Stub mode when pyserial absent. | None |
| **Plate** | `src/biolab/plate.py` | Pure SBS 96-well coordinate math. No hardware deps. | None |
| **Tool Changer** | `src/biolab/tool_changer.py` | 3-tool magnetic dock: pipette, gripper, fridge hook. | arms (for send_action) |
| **Camera** | `src/biolab/camera.py` | Multi-camera capture via OpenCV. Stub mode when cv2 absent. | None |
| **Safety** | `src/biolab/safety.py` | Watchdog, e-stop, joint limits. Pure Python. | None |
| **Dashboard** | `src/dashboard/server.py` | FastAPI server with WebSocket commands and REST status. | All biolab modules |

## Data Flow: Pipetting a Well

```
User/Dashboard → workflow.pipette_well()
  1. arm.send_to_well("arm_a", "TROUGH")  → arms.py → LeRobot (stub: log only)
  2. pipette.aspirate(50.0)                → pipette.py → Arduino serial (stub: track fill)
  3. arm.send_to_well("arm_a", "A1")       → arms.py → plate.py (SBS coords) → LeRobot
  4. pipette.dispense(50.0)                → pipette.py → Arduino serial (stub: track fill)
```

## Data Flow: Tool Change

```
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
| `configs/arms.yaml` | `DualArmConfig.from_yaml()` | Arm ports, motor IDs, camera devices |
| `configs/plate_layout.yaml` | `PlateLayout.from_yaml()` | Workspace origin, Z heights, trough position |
| `configs/tool_dock.yaml` | `ToolDockConfig.from_yaml()` | Joint arrays for 3 dock stations |

## Stub Mode

Every hardware-dependent module gracefully degrades when its dependency is unavailable:

| Module | Trigger | Behavior |
|--------|---------|----------|
| arms.py | `ImportError` on `lerobot` | `send_action` logs and returns; `get_observation` returns `{"stub": True}` |
| pipette.py | `ImportError` on `serial` | Fill state tracked in memory; `_move_to` is a no-op |
| camera.py | `ImportError` on `cv2` | `start()` returns; `get_frames()` returns `{}` |

This allows the full workflow to run end-to-end without any hardware attached. All 92 tests pass in stub mode.

## Key Design Decisions

- **No IK**: `send_to_well()` computes correct (x, y) mm coordinates but sends `[0.0]*6` stub joints. Real inverse kinematics deferred to MVP (requires calibrated hardware).
- **PlateLayout in workflow.py**: Separates pure SBS math (plate.py) from hardware workspace config (workflow.py). Single responsibility.
- **No fridge module**: Fridge joint arrays are constants in workflow.py. YAGNI until hardware exists.
- **Dashboard runs workflow in thread**: `run_workflow` WebSocket command spawns `uc4_demo_all` in a daemon thread to avoid blocking the event loop.
