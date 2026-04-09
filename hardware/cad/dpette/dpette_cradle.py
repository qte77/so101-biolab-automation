"""Rest cradles for AELAB dPette 7016 (single) and DLAB dPette+ (8-channel).

Holds pipette upright at known position. Steel inserts mate with dock magnets.

Usage:
    uv run --group cad python hardware/cad/dpette/dpette_cradle.py
"""

from pathlib import Path

import cadquery as cq

# --- Common parameters (all in mm) ---
WALL = 2.5
BASE_THICKNESS = 4.0
CRADLE_HEIGHT = 30.0
CLEARANCE = 0.5

# dPette 7016 single-channel barrel
SINGLE_BARREL_D = 20.0
SINGLE_OUTER_D = SINGLE_BARREL_D + CLEARANCE * 2 + WALL * 2

# dPette+ 8-channel body (wider, must keep tips level)
MULTI_BODY_W = 50.0
MULTI_BODY_D = 25.0


def build_dpette_single_cradle() -> cq.Workplane:
    """Build rest cradle for dPette 7016 single-channel."""
    # Cylindrical cradle with open top
    outer = cq.Workplane("XY").circle(SINGLE_OUTER_D / 2).extrude(CRADLE_HEIGHT)
    inner = cq.Workplane("XY").circle((SINGLE_BARREL_D + CLEARANCE * 2) / 2).extrude(CRADLE_HEIGHT)
    inner = inner.translate((0, 0, BASE_THICKNESS))
    cradle = outer.cut(inner)

    # Flat base for stability
    base = cq.Workplane("XY").box(SINGLE_OUTER_D + 10, SINGLE_OUTER_D + 10, BASE_THICKNESS)
    return base.union(cradle.translate((0, 0, BASE_THICKNESS / 2)))


def build_dpette_multi_cradle() -> cq.Workplane:
    """Build rest cradle for dPette+ 8-channel (must keep tips level)."""
    inner_w = MULTI_BODY_W + CLEARANCE * 2
    inner_d = MULTI_BODY_D + CLEARANCE * 2
    outer_w = inner_w + WALL * 2
    outer_d = inner_d + WALL * 2

    # Rectangular cradle
    outer = cq.Workplane("XY").box(outer_w, outer_d, CRADLE_HEIGHT + BASE_THICKNESS)
    inner = cq.Workplane("XY").box(inner_w, inner_d, CRADLE_HEIGHT + 1)
    inner = inner.translate((0, 0, BASE_THICKNESS))
    cradle = outer.cut(inner)

    # Wide base for leveling (critical for 8-channel)
    base = cq.Workplane("XY").box(outer_w + 20, outer_d + 20, BASE_THICKNESS)
    return base.union(cradle.translate((0, 0, BASE_THICKNESS / 2)))


def export_single(part: cq.Workplane) -> None:
    stl = Path(__file__).parent.parent.parent / "stl" / "dpette_single_cradle.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "dpette_single_cradle.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")


def export_multi(part: cq.Workplane) -> None:
    stl = Path(__file__).parent.parent.parent / "stl" / "dpette_multi_cradle.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "dpette_multi_cradle.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")


if __name__ == "__main__":
    export_single(build_dpette_single_cradle())
    export_multi(build_dpette_multi_cradle())
