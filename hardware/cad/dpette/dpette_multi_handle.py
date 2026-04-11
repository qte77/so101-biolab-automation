"""dPette+ 8-channel gripper replacement for SO-101.

The SO-101 gripper has two jaws:
  - BOTTOM JAW (fixed, on M5 horn frame) → replaced by PIPETTE CLAMP
  - TOP JAW (on M6 horn, moves) → replaced by EJECTOR LEVER

The robot already provides:
  - M5 wrist rotation (horn = mounting base for clamp)
  - M6 gripper motor (horn = mounting base for lever)
  - Structural wrist housing (holds M6, no cradle needed)

PIPETTE CLAMP (replaces bottom jaw):
  Bolts to M5 horn (4× M3 at 20mm bolt circle).
  Extends out from the horn with a Ø32mm split bore
  to clamp the pipette handle. Manifold + nozzles hang below.

EJECTOR LEVER (replaces top jaw):
  Bolts to M6 horn (25T spline + 4× M2 at 16mm bolt circle).
  When M6 rotates (like closing the gripper), the lever sweeps
  and pushes DOWN on the ejector hook.
  Short arm (20mm) → ~175N from 35 kg·cm stall torque.

Usage:
    uv run --group cad python hardware/cad/dpette/dpette_multi_handle.py
"""

import math
from pathlib import Path

import cadquery as cq

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


def build_dpette_multi_handle() -> cq.Workplane:
    """Pipette clamp — replaces SO-101 bottom jaw.

    Bolts to M5 horn. Extends outward. Ø32mm split bore at the end.
    """
    # Main body — extends from horn mount to bore
    body = cq.Workplane("XY").box(CLAMP_LENGTH, CLAMP_WIDTH, CLAMP_THICK)
    # Shift so horn end is at X=0, bore end at X=+CLAMP_LENGTH
    body = body.translate((CLAMP_LENGTH / 2, 0, 0))

    # --- Horn end (X=0): M5 horn bolt holes ---
    for i in range(4):
        a = math.radians(i * 90 + 45)
        bx = M5_BOLT_CIRCLE / 2 * math.cos(a)
        by = M5_BOLT_CIRCLE / 2 * math.sin(a)
        h = cq.Workplane("XY").circle(M3 / 2).extrude(CLAMP_THICK + 2)
        body = body.cut(h.translate((bx, by, -1)))

    # Horn center hole (shaft clearance)
    shaft = cq.Workplane("XY").circle(7).extrude(CLAMP_THICK + 2)
    body = body.cut(shaft.translate((0, 0, -1)))

    # --- Bore end (X=CLAMP_LENGTH): Ø32mm split clamp ---
    bore_x = CLAMP_LENGTH

    # Clamp ring (hangs below plate, wraps around handle)
    ring_h = 18.0
    ring_od = HANDLE_DIA + CL * 2 + CLAMP_WALL * 2
    ring = cq.Workplane("XY").circle(ring_od / 2).extrude(ring_h)
    ring_bore = cq.Workplane("XY").circle((HANDLE_DIA + CL * 2) / 2).extrude(ring_h + 2)
    ring = ring.cut(ring_bore.translate((0, 0, -1)))
    ring = ring.translate((bore_x, 0, -ring_h + CLAMP_THICK / 2))
    body = body.union(ring)

    # Cut bore through the ENTIRE height (plate + ring) so pipette passes through
    full_bore = cq.Workplane("XY").circle((HANDLE_DIA + CL * 2) / 2).extrude(ring_h + CLAMP_THICK + 4)
    body = body.cut(full_bore.translate((bore_x, 0, -ring_h - 2)))

    # Split in clamp ring ONLY (not through plate — plate holds halves together)
    split = cq.Workplane("XY").box(1.5, ring_od + 2, ring_h)
    body = body.cut(split.translate((bore_x, 0, -CLAMP_THICK / 2 - ring_h / 2)))

    # Pinch bolts (2× M3, through clamp in Y direction)
    for x_off in [-8, 8]:
        pinch = (
            cq.Workplane("XY").circle(CLAMP_BOLT / 2).extrude(ring_od + 10)
            .rotateAboutCenter((1, 0, 0), 90)
            .translate((bore_x + x_off, 0, -ring_h / 2 + CLAMP_THICK / 2))
        )
        body = body.cut(pinch)

    return body


def build_ejector_lever() -> cq.Workplane:
    """Ejector lever — replaces SO-101 top jaw.

    Bolts to M6 horn. When M6 rotates (gripper close motion),
    the lever sweeps and the finger pushes DOWN on the ejector hook.

    Force budget: 35 kg·cm / 2.0 cm = 175N (needs ~100N for 8 tips).
    """
    # Horn disc (M6 25T spline)
    horn = cq.Workplane("XY").circle(M6_HORN_DIA / 2).extrude(M6_HORN_THICK)
    horn = horn.faces(">Z").workplane().hole(M6_HORN_BORE)

    # Horn bolt holes (4× M2 at 16mm bolt circle)
    for i in range(4):
        a = math.radians(i * 90)
        hx = M6_BOLT_CIRCLE / 2 * math.cos(a)
        hy = M6_BOLT_CIRCLE / 2 * math.sin(a)
        bh = cq.Workplane("XY").circle(M6_HORN_SCREW / 2).extrude(M6_HORN_THICK + 2)
        horn = horn.cut(bh.translate((hx, hy, -1)))

    # Lever arm — extends radially from horn
    arm = cq.Workplane("XY").box(LEVER_W, LEVER_ARM, LEVER_T)
    arm_y = M6_HORN_DIA / 2 + LEVER_ARM / 2 - 2
    arm = arm.translate((0, arm_y, LEVER_T / 2))

    # Downward finger at tip — pushes ejector hook
    finger_y = M6_HORN_DIA / 2 + LEVER_ARM - 2
    finger = cq.Workplane("XY").box(LEVER_W, LEVER_T, FINGER_H)
    finger = finger.translate((0, finger_y, -FINGER_H / 2 + LEVER_T / 2))

    # Rounded contact pad at bottom of finger (cylinder, not sphere — cleaner mesh)
    pad = cq.Workplane("XY").circle(LEVER_W / 2).extrude(3)
    pad = pad.translate((0, finger_y, -FINGER_H + LEVER_T / 2 - 3))

    return horn.union(arm).union(finger).union(pad)


def export(part: cq.Workplane, name: str) -> None:
    base = Path(__file__).parent.parent.parent
    stl = base / "stl" / "dpette" / f"{name}.stl"
    svg = base / "svg" / "dpette" / f"{name}.svg"
    stl.parent.mkdir(parents=True, exist_ok=True)
    svg.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {name}")


if __name__ == "__main__":
    export(build_dpette_multi_handle(), "dpette_multi_handle")
    export(build_ejector_lever(), "dpette_ejector_lever")
