"""dPette+ 8-channel gripper replacement for SO-101.

The SO-101 gripper has two jaws:
  - BOTTOM JAW (fixed, on M5 horn frame) -> replaced by PIPETTE CLAMP
  - TOP JAW (on M6 horn, moves)           -> replaced by EJECTOR LEVER

The robot already provides:
  - M5 wrist rotation (horn = mounting base for clamp)
  - M6 gripper motor (horn = mounting base for lever)
  - Structural wrist housing (holds M6, no cradle needed)

PIPETTE CLAMP (replaces bottom jaw):
  Bolts to M5 horn (4x M3 at 20mm bolt circle).
  Extends out from the horn with a Ø32mm split bore
  to clamp the pipette handle. Manifold + nozzles hang below.

EJECTOR LEVER (replaces top jaw):
  Bolts to M6 horn (25T spline + 4x M2 at 16mm bolt circle).
  When M6 rotates (like closing the gripper), the lever sweeps
  and pushes DOWN on the ejector hook.
  Short arm (20mm) -> ~175N from 35 kg-cm stall torque.

Usage:
    uv run --group cad python app/hardware/cad/dpette/dpette_multi_handle.py

Ported from Antonio Lamb's CadQuery source (PR #48) to build123d.
Geometry preserved from the 3D-scan-verified redesign. Cylinder
placements use intent-based positioning (hole/ring at nominal target)
rather than byte-matching CadQuery's extrude-from-zero +
rotateAboutCenter semantics.
"""

import math
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot

sys.path.append(str(Path(__file__).resolve().parent.parent))
from util.export import export_part

sys.path.pop()

# --- STS3215 servo horn dimensions ---
# M5 horn (wrist — where bottom jaw mounts)
M5_BOLT_CIRCLE = 20.0
M3 = 3.2  # M3 clearance

# M6 horn (gripper — where top jaw mounts)
M6_HORN_DIA = 24.0
M6_HORN_BORE = 6.0
M6_HORN_THICK = 3.0
M6_HORN_SCREW = 2.2  # M2 clearance
M6_BOLT_CIRCLE = 16.0

# --- dPette+ handle (3D scan verified) ---
HANDLE_DIA = 32.0  # Round Ø32mm
CL = 0.3           # Clearance per side

# --- Pipette clamp dims ---
CLAMP_LENGTH = 50.0   # Extension from horn center to bore center
CLAMP_WIDTH = 42.0    # Wide enough for Ø32 bore + walls
CLAMP_THICK = 8.0     # Z thickness — rigid
CLAMP_WALL = 5.0      # Wall around bore
CLAMP_BOLT = 3.2      # M3 pinch bolts

# --- Ejector lever dims ---
LEVER_ARM = 20.0    # Horn center to contact tip (short = more force)
LEVER_W = 10.0      # Width
LEVER_T = 6.0       # Thickness
FINGER_H = 15.0     # Downward reach of contact finger

# Derived
RING_H = 18.0
RING_OD = HANDLE_DIA + CL * 2 + CLAMP_WALL * 2
RING_BORE = HANDLE_DIA + CL * 2
# Ring top flush with plate top (z = CLAMP_THICK/2), ring extends downward
RING_Z_CENTER = CLAMP_THICK / 2 - RING_H / 2


def build_dpette_multi_handle():
    """Pipette clamp — replaces SO-101 bottom jaw.

    Bolts to M5 horn at (0,0), extends outward along +X, Ø32mm split
    bore at (+CLAMP_LENGTH, 0). Clamp ring hangs below the plate.
    """
    # Main body plate — body spans x from 0 to CLAMP_LENGTH
    body = Pos(CLAMP_LENGTH / 2, 0, 0) * Box(CLAMP_LENGTH, CLAMP_WIDTH, CLAMP_THICK)

    # Horn end: 4x M3 clearance holes on 20mm bolt circle
    for i in range(4):
        a = math.radians(i * 90 + 45)
        bx = M5_BOLT_CIRCLE / 2 * math.cos(a)
        by = M5_BOLT_CIRCLE / 2 * math.sin(a)
        body = body - (Pos(bx, by, 0) * Cylinder(M3 / 2, CLAMP_THICK + 2))

    # Horn centre: shaft clearance hole
    body = body - (Pos(0, 0, 0) * Cylinder(7.0, CLAMP_THICK + 2))

    # Clamp ring at bore end — top flush with plate top, extends downward
    bore_x = CLAMP_LENGTH
    ring_outer = Pos(bore_x, 0, RING_Z_CENTER) * Cylinder(RING_OD / 2, RING_H)
    body = body + ring_outer

    # Cut bore through the full height (plate + ring) so pipette passes through
    full_bore_h = RING_H + CLAMP_THICK + 4
    full_bore = Pos(bore_x, 0, RING_Z_CENTER) * Cylinder(RING_BORE / 2, full_bore_h)
    body = body - full_bore

    # Split in the lower portion of the ring (bottom half only — plate top holds halves together)
    split_z = -CLAMP_THICK / 2 - RING_H / 2 + RING_H / 2  # = -CLAMP_THICK/2 (top of split coincides with ring top half)
    split = Pos(bore_x, 0, split_z - RING_H / 4) * Box(1.5, RING_OD + 2, RING_H / 2)
    body = body - split

    # 2x M3 pinch bolts — horizontal through the ring along Y, at ring mid-height
    for x_off in (-8, 8):
        pinch = (
            Pos(bore_x + x_off, 0, RING_Z_CENTER)
            * Rot(90, 0, 0)
            * Cylinder(CLAMP_BOLT / 2, RING_OD + 10)
        )
        body = body - pinch

    return body


def build_ejector_lever():
    """Ejector lever — replaces SO-101 top jaw.

    Bolts to M6 horn. When M6 rotates (gripper-close motion), the lever
    sweeps and the finger pushes down on the ejector hook.

    Force budget: 35 kg-cm / 2.0 cm = 175N (needs ~100N for 8 tips).
    """
    # Horn disc
    horn = Pos(0, 0, M6_HORN_THICK / 2) * Cylinder(M6_HORN_DIA / 2, M6_HORN_THICK)

    # Centre bore for M6 spline
    bore = Pos(0, 0, M6_HORN_THICK / 2) * Cylinder(M6_HORN_BORE / 2, M6_HORN_THICK + 2)
    horn = horn - bore

    # 4x M2 horn bolt pattern on 16mm BC
    for i in range(4):
        a = math.radians(i * 90)
        hx = M6_BOLT_CIRCLE / 2 * math.cos(a)
        hy = M6_BOLT_CIRCLE / 2 * math.sin(a)
        horn = horn - (Pos(hx, hy, M6_HORN_THICK / 2) * Cylinder(M6_HORN_SCREW / 2, M6_HORN_THICK + 2))

    # Lever arm — straight, along +Y from the horn edge
    arm_y = M6_HORN_DIA / 2 + LEVER_ARM / 2 - 2
    arm = Pos(0, arm_y, LEVER_T / 2) * Box(LEVER_W, LEVER_ARM, LEVER_T)

    # Downward finger at the arm tip — pushes ejector hook
    finger_y = M6_HORN_DIA / 2 + LEVER_ARM - 2
    finger = Pos(0, finger_y, -FINGER_H / 2 + LEVER_T / 2) * Box(LEVER_W, LEVER_T, FINGER_H)

    # Contact pad at the bottom of the finger (cylinder, clean mesh)
    pad_thick = 3.0
    pad = Pos(0, finger_y, -FINGER_H + LEVER_T / 2 - pad_thick / 2) * Cylinder(LEVER_W / 2, pad_thick)

    return horn + arm + finger + pad


if __name__ == "__main__":
    export_part(build_dpette_multi_handle(), "dpette", "dpette_multi_handle")
    export_part(build_ejector_lever(), "dpette", "dpette_ejector_lever")
