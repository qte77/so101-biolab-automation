---
title: STL Files Index
purpose: Index of 3D-printable parts with status, print settings, and source scripts
created: 2026-03-27
updated: 2026-03-27
---

# STL Files

All STL files are generated from CadQuery scripts in `../cad/`. Run `make render_parts` to regenerate.

**Status legend:** EXPERIMENTAL = draft dimensions, untested. VALIDATED = printed and tested on hardware.

## Print Settings (Default)

- Material: PLA+
- Nozzle: 0.4mm
- Layer height: 0.2mm
- Infill: 15%
- Supports: >45° from horizontal

Exception: `gripper_tips_tpu.stl` — print in TPU 95A.

## Parts

| STL File | Status | CadQuery Source | Description |
|----------|--------|-----------------|-------------|
| `96well_plate_holder.stl` | EXPERIMENTAL | `../cad/plate_holder.py` | SBS footprint (127.76 × 85.48 mm) with alignment pins |
| `tool_cone_robot.stl` | EXPERIMENTAL | `../cad/tool_changer.py` | Female cone adapter for SO-101 wrist (motor 5 horn) |
| `tool_cone_pipette.stl` | EXPERIMENTAL | `../cad/tool_changer.py` | Male cone base for pipette tool |
| `tool_cone_gripper.stl` | EXPERIMENTAL | `../cad/tool_changer.py` | Male cone base for stock gripper |
| `tool_cone_hook.stl` | EXPERIMENTAL | `../cad/tool_changer.py` | Male cone base for fridge hook |
| `tool_dock_3station.stl` | EXPERIMENTAL | `../cad/tool_dock.py` | 3-slot parking rack with magnets |
| `pipette_mount_so101.stl` | EXPERIMENTAL | `../cad/pipette_mount.py` | Gripper-to-pipette body adapter |
| `fridge_hook_tool.stl` | EXPERIMENTAL | `../cad/fridge_hook.py` | Hook end-effector for fridge door |
| `tip_rack_holder.stl` | EXPERIMENTAL | `../cad/tip_rack_holder.py` | Pipette tip rack mount |
| `gripper_tips_tpu.stl` | EXPERIMENTAL | `../cad/gripper_tips.py` | Compliant fingertips (TPU 95A) |

## SVG Previews

2D projections of each part are in `../svg/` for documentation. Generated alongside STL by `make render_parts`.
