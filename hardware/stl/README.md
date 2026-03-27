---
title: STL Files Index
purpose: Index of 3D-printable parts with status, print settings, assembly, and source scripts
created: 2026-03-27
updated: 2026-03-27
---

# STL Files

Generated from CadQuery scripts in `../cad/`. Run `make render_parts` to regenerate (requires Python 3.10 + `make setup_cad`).

**Status:** EXPERIMENTAL = draft dimensions, untested on hardware.

## Print Settings

| Setting | Default | Exception |
|---------|---------|-----------|
| Material | PLA+ | `gripper_tips_tpu.stl` → TPU 95A |
| Nozzle | 0.4mm | — |
| Layer height | 0.2mm | — |
| Infill | 15% | — |
| Supports | >45° | — |

## Parts & Assembly

### Tool Changer System

Passive tool changing based on [Berkeley design](https://goldberg.berkeley.edu/pubs/CASE2018-ron-tool-changer-submitted.pdf) (truncated cone + dowel pins + magnets).

**Assembly order:**

1. **`tool_cone_robot.stl`** — Mount on SO-101 wrist (motor 5 horn, 4× M3 screws). This stays on the arm permanently.
2. **`tool_cone_pipette/gripper/hook.stl`** — Attach one to each tool (pipette body, stock gripper, fridge hook). Glue or screw to tool base.
3. **`tool_dock_3station.stl`** — Fix to workspace (table clamp or screws). Insert 5mm neodymium magnets in each slot bottom. Place tools in slots when not in use.

**Tool change sequence:** Arm approaches dock → inserts current tool into slot → retracts → moves to new tool slot → pushes onto cone → retracts with new tool.

### Pipette Setup

1. **`pipette_mount_so101.stl`** — Clamp around [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2) barrel. Tighten with 2× M3 screws through side holes.
2. Attach `tool_cone_pipette.stl` to the mount's flat base (4× M3 or glue).
3. **`tip_rack_holder.stl`** — Place on workspace, insert standard tip rack. Arm picks up tips by pressing pipette into rack.

### Plate Handling

1. **`96well_plate_holder.stl`** — Place on workspace at known position. 4 alignment pins locate the plate. Arm places/retrieves plates from this holder.

### Fridge Operations

1. **`fridge_hook_tool.stl`** — Attach `tool_cone_hook.stl` to the flat mount face. Hook opening fits standard lab fridge handles (~20mm bar).
2. Arm equips hook from dock → approaches fridge → hooks handle → pulls door open.

### Gripper Enhancement

1. **`gripper_tips_tpu.stl`** — Press-fit or glue onto SO-101 stock gripper fingers. Grip ridges improve hold on smooth labware.

## Parts Table

| STL File | Source | Description |
|----------|--------|-------------|
| `tool_cone_robot.stl` | `tool_changer.py` | Female cone — mounts on SO-101 wrist |
| `tool_cone_pipette.stl` | `tool_changer.py` | Male cone — pipette tool base |
| `tool_cone_gripper.stl` | `tool_changer.py` | Male cone — gripper tool base |
| `tool_cone_hook.stl` | `tool_changer.py` | Male cone — fridge hook tool base |
| `tool_dock_3station.stl` | `tool_dock.py` | 3-slot parking rack with magnet pockets |
| `pipette_mount_so101.stl` | `pipette_mount.py` | Barrel clamp for digital-pipette-v2 |
| `96well_plate_holder.stl` | `plate_holder.py` | SBS plate holder with alignment pins |
| `fridge_hook_tool.stl` | `fridge_hook.py` | Hook for fridge door handle |
| `tip_rack_holder.stl` | `tip_rack_holder.py` | Tip rack tray |
| `gripper_tips_tpu.stl` | `gripper_tips.py` | Compliant fingertips (print in TPU 95A) |

## SVG Previews

2D projections in `../svg/`. Generated alongside STL by `make render_parts`.

## Hardware Needed (Non-Printed)

- 5mm × 3mm neodymium magnets (3 for dock, 4 for cone pairs)
- M3 × 8mm screws (4 for wrist mount, 2 per pipette clamp)
- Glue (CA or epoxy) for cone-to-tool bonding
