"""dPette+ mount bracket + cam arm for SO-101.

Two printed parts:
  1. U-bracket mount — top bar bolts to M5 horn, vertical side holds M6
     motor, bottom bar clamps pipette barrel. Rigid frame, no flex.
  2. Straight cam arm — on M6 horn, sweeps sideways into ejector hook.

Side view (matches draw.io diagram):

    ════════════════════  ← top bar (bolts to M5 horn)
    ║                  ║
    ║  [M6]----arm     ║  ← vertical side (holds motor)
    ║                  ║
    ════════════════════  ← bottom bar (clamps barrel)
         │ pipette │
         │  body   │
         └────────┘

Motor dims: STS3215 = 45.2 x 24.7 x 35 mm, 25T spline, M2 mount.

Usage:
    uv run --group cad python hardware/cad/dpette/dpette_handle.py
"""

import math
from pathlib import Path

import cadquery as cq

# --- STS3215 servo ---
MOTOR_W = 24.7
MOTOR_L = 45.2
MOTOR_H = 35.0
M2 = 2.2
HORN_DIA = 24.0
HORN_BORE = 6.0
HORN_THICK = 3.0
HORN_SCREW = 2.2
HORN_BOLT_CIRCLE = 16.0

# --- dPette+ barrel ---
BARREL_D = 20.0
BARREL_CL = 0.3

# --- U-bracket dims ---
BAR_W = 80.0              # Width of top and bottom bars (X)
BAR_D = 38.0              # Depth of bars (Y)
BAR_T = 5.0               # Thickness of bars (Z)
SIDE_W = 5.0              # Vertical side wall thickness (X)
SIDE_H = 50.0             # Distance between top and bottom bars (Z)

# --- Positions ---
MOTOR_X = -15.0           # Motor offset in bracket
BARREL_X = 18.0           # Barrel offset in bracket

# --- M5 horn bolt pattern (top bar) ---
M5_BOLT_CIRCLE = 20.0
M3 = 3.2

# --- Barrel clamp (bottom bar) ---
CLAMP_BOLT = 3.2

# --- Straight cam arm ---
CAM_LENGTH = 32.0
CAM_W = 6.0
CAM_T = 4.0
CAM_TIP_R = 2.0


def build_mount_bracket() -> cq.Workplane:
    """U-bracket: top bar + vertical side + bottom bar."""
    # Top bar
    top = cq.Workplane("XY").box(BAR_W, BAR_D, BAR_T)
    top = top.translate((0, 0, SIDE_H + BAR_T / 2))

    # Bottom bar
    bot = cq.Workplane("XY").box(BAR_W, BAR_D, BAR_T)
    bot = bot.translate((0, 0, -BAR_T / 2))

    # Vertical side (right side, connects top and bottom)
    side_x = BAR_W / 2 - SIDE_W / 2
    side = cq.Workplane("XY").box(SIDE_W, BAR_D, SIDE_H)
    side = side.translate((side_x, 0, SIDE_H / 2))

    bracket = top.union(bot).union(side)

    # --- Top bar: M5 horn bolt holes ---
    for i in range(4):
        a = math.radians(i * 90 + 45)
        bx = M5_BOLT_CIRCLE / 2 * math.cos(a)
        by = M5_BOLT_CIRCLE / 2 * math.sin(a)
        h = cq.Workplane("XY").circle(M3 / 2).extrude(BAR_T + 2)
        bracket = bracket.cut(h.translate((bx, by, SIDE_H)))

    # --- Top bar: motor 6 pocket (recessed from underside) ---
    pocket = cq.Workplane("XY").box(MOTOR_W + 1, MOTOR_L + 1, BAR_T + 1)
    bracket = bracket.cut(pocket.translate((MOTOR_X, 0, SIDE_H + BAR_T / 2)))

    # Motor horn shaft hole (through top bar)
    horn_exit = cq.Workplane("XY").circle(HORN_DIA / 2 + 1).extrude(BAR_T + 2)
    bracket = bracket.cut(horn_exit.translate((MOTOR_X, 0, SIDE_H)))

    # Motor mount holes (2x M2 through vertical side)
    motor_z = SIDE_H - MOTOR_H / 2
    for z_off in [-8, 8]:
        h = (
            cq.Workplane("XY").circle(M2 / 2).extrude(SIDE_W + 10)
            .rotateAboutCenter((0, 1, 0), 90)
            .translate((side_x, 0, motor_z + z_off))
        )
        bracket = bracket.cut(h)

    # --- Bottom bar: barrel bore ---
    bore = cq.Workplane("XY").circle((BARREL_D + BARREL_CL * 2) / 2).extrude(BAR_T + 2)
    bracket = bracket.cut(bore.translate((BARREL_X, 0, -BAR_T - 1)))

    # Barrel pinch bolt (through bottom bar, Y direction)
    pinch = (
        cq.Workplane("XY").circle(CLAMP_BOLT / 2).extrude(BAR_D + 10)
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((BARREL_X, 0, -BAR_T / 2))
    )
    bracket = bracket.cut(pinch)

    # Bottom bar split (so barrel can be clamped)
    split = cq.Workplane("XY").box(1.5, BAR_D + 2, BAR_T + 2)
    bracket = bracket.cut(split.translate((BARREL_X, 0, -BAR_T / 2)))

    return bracket


def build_cam_arm() -> cq.Workplane:
    """Straight radial arm on M6 horn. Sweeps into ejector hook."""
    # Horn disc
    horn = cq.Workplane("XY").circle(HORN_DIA / 2).extrude(HORN_THICK)
    horn = horn.faces(">Z").workplane().hole(HORN_BORE)
    horn = horn.faces(">Z").workplane().hole(HORN_SCREW)

    for i in range(4):
        a = math.radians(i * 90)
        hx = HORN_BOLT_CIRCLE / 2 * math.cos(a)
        hy = HORN_BOLT_CIRCLE / 2 * math.sin(a)
        bh = cq.Workplane("XY").circle(HORN_SCREW / 2).extrude(HORN_THICK + 2)
        horn = horn.cut(bh.translate((hx, hy, -1)))

    # Straight arm
    arm = cq.Workplane("XY").box(CAM_W, CAM_LENGTH, CAM_T)
    arm_y = HORN_DIA / 2 + CAM_LENGTH / 2 - 2
    arm = arm.translate((0, arm_y, CAM_T / 2))

    # Rounded contact tip
    tip = cq.Workplane("XY").sphere(CAM_TIP_R)
    tip_y = HORN_DIA / 2 + CAM_LENGTH - 2
    tip = tip.translate((0, tip_y, CAM_T / 2))

    return horn.union(arm).union(tip)


def export(part: cq.Workplane, name: str) -> None:
    base = Path(__file__).parent.parent.parent
    stl = base / "stl" / "dpette" / f"{name}.stl"
    svg = base / "svg" / "dpette" / f"{name}.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {name}")


if __name__ == "__main__":
    export(build_mount_bracket(), "dpette_handle")
    export(build_cam_arm(), "dpette_cam_arm")
