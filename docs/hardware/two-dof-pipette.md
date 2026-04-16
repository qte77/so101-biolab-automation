---
title: 2-DOF Pipette Mode (SO-101 Variant)
purpose: Use SO-101 as a 2-axis positioner with fixed pipette mount — shoulder_pan + shoulder_lift only
authority: Variant configuration (INFORMATIONAL — references bringup.md and architecture.md)
created: 2026-04-14
---

# 2-DOF Pipette Mode

Alternate SO-101 configuration: **use only shoulder_pan + shoulder_lift** (joints
1 and 2) as a 2-axis positioner. A fixed pipette mount replaces the lower arm
(elbow, wrist, gripper) for simple pipetting workflows.

For standard 6-DOF bringup, see [bringup.md](bringup.md).
For roadmap context, see [../roadmap.md](../roadmap.md).

## Rationale

- Pipetting often only needs **reach + height** — elbow/wrist articulation is
  unnecessary overhead
- Electronic pipette (USB-controlled) handles aspirate/dispense — no servo needed
  for plunger
- Simpler kinematics, smaller workspace, cheaper spares (fewer moving servos)

## Mechanical

- Pipette mount attaches **to the upper arm** (post-shoulder, pre-elbow region)
- Lower arm (servos 3-6) either:
  - **Removed entirely** — need mechanical plug/cap at upper arm end
  - **Left attached, parked** — servos 3-6 hold a fixed pose; simplest, no
    structural changes
- Electronic pipette (e.g. AELAB dPette 7016, DLAB dPette+) plugged via USB
  directly to the host PC — plunger actuation is independent of SO-101 servos

## LeRobot Integration Options

LeRobot's `SOFollower` hardcodes all 6 servos in `__init__` (see
`.venv/lib/python3.12/site-packages/lerobot/robots/so_follower/so_follower.py:54-61`).
Three ways to use it with fewer motors:

### Option A — Skip lerobot, use scservo_sdk directly (recommended)

Minimal 2-servo controller in `app/so101/two_dof_arm.py` talking directly to
`scservo_sdk.PacketHandler`. No patches needed. No 6-DOF infrastructure.

**Pros:** Clean, minimal, no lerobot coupling.
**Cons:** No free policy training / episode recording / teleop (but for fixed
pipette mode, leader-follower teleop doesn't make much sense anyway).

### Option B — Patch `SOFollower` to use only 2 motors

Add a 4th patch to `app/so101/patch_lerobot.py` that rewrites the motor
dict in `SOFollower.__init__` to only `shoulder_pan` and `shoulder_lift`.

**Pros:** Reuse `lerobot-calibrate`, `lerobot-teleoperate`, etc.
**Cons:** Another installed-package patch to maintain. Calibration files from
this mode won't match 6-DOF files.

### Option C — Subclass in our project

Create `app/so101/two_dof_follower.py` that inherits `SOFollower` and overrides
`__init__` with only the 2 motors. Used via our `DualArmController`, not
lerobot CLI.

**Pros:** No upstream patch; clean separation.
**Cons:** Loses lerobot CLI compatibility (can't use `lerobot-teleoperate`
unless we also register a custom robot type with draccus).

## Plunger Actuation

Electronic pipette USB protocols are backend-specific. See `app/so101/pipette.py`
(skeleton) and the BOM for recommended models (AELAB dPette 7016 single-channel,
DLAB dPette+ 8-channel).

## Recalibration

If swapping from gripper to pipette mount changes joint 1-2 offsets (e.g. the
mount shifts center of mass or adds a lever arm that affects homing), rerun
`lerobot-calibrate` for just those joints (requires Option B or C).

Otherwise, standard 6-DOF calibration is fine — joints 3-6 hold their park pose
and are never commanded to move.

## Known Constraints

- **Workspace** — limited to a cylindrical sector defined by arm length,
  shoulder_pan range, and shoulder_lift range (no Z-reach beyond the fixed arm
  length)
- **Tip pickup** — pipette must press into tip rack by moving the whole arm
  (shoulder_lift down); no independent Z-axis
- **Tip ejection** — electronic pipette's built-in ejector button (manual or
  USB command) since there's no gripper servo to drive the ejector lever
