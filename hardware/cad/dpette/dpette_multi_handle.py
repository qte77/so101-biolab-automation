"""dPette+ 8-channel U-bracket mount for SO-101.

Same U-bracket as single-channel but with rectangular bore in bottom
bar for the 50x25mm 8-channel body. Nozzles are FIXED (no rotation).
Shares the same straight cam arm (from dpette_handle.py).

Usage:
    uv run --group cad python hardware/cad/dpette/dpette_multi_handle.py
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

# --- dPette+ 8-channel body (nozzles fixed) ---
BODY_W = 50.0
BODY_D = 25.0
CL = 0.4

# --- U-bracket ---
BAR_W = 90.0
BAR_D = 50.0
BAR_T = 5.0
SIDE_W = 5.0
SIDE_H = 55.0

# --- Positions ---
MOTOR_X = -18.0
BODY_X = 15.0

M5_BOLT_CIRCLE = 20.0
M3 = 3.2
CLAMP_BOLT = 3.2


def build_dpette_multi_handle() -> cq.Workplane:
    """U-bracket: top bar + vertical side + bottom bar with rect bore."""
    top = cq.Workplane("XY").box(BAR_W, BAR_D, BAR_T)
    top = top.translate((0, 0, SIDE_H + BAR_T / 2))

    bot = cq.Workplane("XY").box(BAR_W, BAR_D, BAR_T)
    bot = bot.translate((0, 0, -BAR_T / 2))

    side_x = BAR_W / 2 - SIDE_W / 2
    side = cq.Workplane("XY").box(SIDE_W, BAR_D, SIDE_H)
    side = side.translate((side_x, 0, SIDE_H / 2))

    bracket = top.union(bot).union(side)

    # M5 horn bolt holes (top bar)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        bx = M5_BOLT_CIRCLE / 2 * math.cos(a)
        by = M5_BOLT_CIRCLE / 2 * math.sin(a)
        h = cq.Workplane("XY").circle(M3 / 2).extrude(BAR_T + 2)
        bracket = bracket.cut(h.translate((bx, by, SIDE_H)))

    # Motor 6 pocket (top bar underside)
    pocket = cq.Workplane("XY").box(MOTOR_W + 1, MOTOR_L + 1, BAR_T + 1)
    bracket = bracket.cut(pocket.translate((MOTOR_X, 0, SIDE_H + BAR_T / 2)))

    # Horn shaft hole
    horn_exit = cq.Workplane("XY").circle(HORN_DIA / 2 + 1).extrude(BAR_T + 2)
    bracket = bracket.cut(horn_exit.translate((MOTOR_X, 0, SIDE_H)))

    # Motor mount holes (through side)
    motor_z = SIDE_H - MOTOR_H / 2
    for z_off in [-8, 8]:
        h = (
            cq.Workplane("XY").circle(M2 / 2).extrude(SIDE_W + 10)
            .rotateAboutCenter((0, 1, 0), 90)
            .translate((side_x, 0, motor_z + z_off))
        )
        bracket = bracket.cut(h)

    # Bottom bar: rectangular bore for 8-channel body
    bore = cq.Workplane("XY").box(BODY_W + CL * 2, BODY_D + CL * 2, BAR_T + 2)
    bracket = bracket.cut(bore.translate((BODY_X, 0, -BAR_T / 2)))

    # Pinch bolts (2x M3, through bottom bar Y direction)
    for x_off in [-BODY_W / 4, BODY_W / 4]:
        pinch = (
            cq.Workplane("XY").circle(CLAMP_BOLT / 2).extrude(BAR_D + 10)
            .rotateAboutCenter((1, 0, 0), 90)
            .translate((BODY_X + x_off, 0, -BAR_T / 2))
        )
        bracket = bracket.cut(pinch)

    # Split in bottom bar
    split = cq.Workplane("XY").box(1.5, BAR_D + 2, BAR_T + 2)
    bracket = bracket.cut(split.translate((BODY_X, 0, -BAR_T / 2)))

    return bracket


def export(part: cq.Workplane) -> None:
    base = Path(__file__).parent.parent.parent
    stl = base / "stl" / "dpette" / "dpette_multi_handle.stl"
    svg = base / "svg" / "dpette" / "dpette_multi_handle.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: dpette_multi_handle")


if __name__ == "__main__":
    export(build_dpette_multi_handle())
