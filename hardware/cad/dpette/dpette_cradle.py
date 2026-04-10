"""Rest cradles for AELAB dPette 7016 (single) and DLAB dPette+ (8-channel).

Holds pipette upright at known position. Steel inserts mate with dock magnets.

Usage:
    uv run --group cad python hardware/cad/dpette/dpette_cradle.py
"""

from pathlib import Path

from build123d import Box, Cylinder, ExportSVG, Pos, export_stl

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


def build_dpette_single_cradle():
    """Build rest cradle for dPette 7016 single-channel."""
    # Cylindrical cradle with open top
    outer = Cylinder(SINGLE_OUTER_D / 2, CRADLE_HEIGHT)
    inner = Pos(0, 0, BASE_THICKNESS) * Cylinder(
        (SINGLE_BARREL_D + CLEARANCE * 2) / 2, CRADLE_HEIGHT
    )
    cradle = outer - inner

    # Flat base for stability
    base = Box(SINGLE_OUTER_D + 10, SINGLE_OUTER_D + 10, BASE_THICKNESS)
    return base + Pos(0, 0, BASE_THICKNESS / 2) * cradle


def build_dpette_multi_cradle():
    """Build rest cradle for dPette+ 8-channel (must keep tips level)."""
    inner_w = MULTI_BODY_W + CLEARANCE * 2
    inner_d = MULTI_BODY_D + CLEARANCE * 2
    outer_w = inner_w + WALL * 2
    outer_d = inner_d + WALL * 2

    # Rectangular cradle
    outer = Box(outer_w, outer_d, CRADLE_HEIGHT + BASE_THICKNESS)
    inner = Pos(0, 0, BASE_THICKNESS) * Box(inner_w, inner_d, CRADLE_HEIGHT + 1)
    cradle = outer - inner

    # Wide base for leveling (critical for 8-channel)
    base = Box(outer_w + 20, outer_d + 20, BASE_THICKNESS)
    return base + Pos(0, 0, BASE_THICKNESS / 2) * cradle


def export_single(part) -> None:
    stl = Path(__file__).parent.parent.parent / "stl" / "dpette" / "dpette_single_cradle.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "dpette" / "dpette_single_cradle.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")


def export_multi(part) -> None:
    stl = Path(__file__).parent.parent.parent / "stl" / "dpette" / "dpette_multi_cradle.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "dpette" / "dpette_multi_cradle.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")


if __name__ == "__main__":
    export_single(build_dpette_single_cradle())
    export_multi(build_dpette_multi_cradle())
