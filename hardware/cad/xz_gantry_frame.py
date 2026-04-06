"""XZ gantry bridge frame — bracket pair for 2020 aluminium extrusion.

Spans mini cooler to PCR block (~300mm). Two identical brackets hold
the X-axis rail. Designed for M5 T-slot bolts.

Usage:
    uv run --group cad python hardware/cad/xz_gantry_frame.py
"""

from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
BRACKET_WIDTH = 40.0
BRACKET_HEIGHT = 60.0
BRACKET_DEPTH = 30.0
WALL = 4.0
EXTRUSION_SLOT = 20.0  # 2020 profile
BOLT_HOLE_D = 5.2  # M5 clearance
RAIL_MOUNT_HOLES = 3.2  # M3 for MGN12 rail


def build_xz_gantry_frame() -> cq.Workplane:
    """Build one L-bracket for XZ gantry frame."""
    # Vertical plate (holds rail)
    vertical = cq.Workplane("XY").box(BRACKET_WIDTH, WALL, BRACKET_HEIGHT)
    vertical = vertical.translate((0, -BRACKET_DEPTH / 2 + WALL / 2, BRACKET_HEIGHT / 2))

    # Horizontal base (bolts to extrusion or table)
    base = cq.Workplane("XY").box(BRACKET_WIDTH, BRACKET_DEPTH, WALL)

    bracket = base.union(vertical)

    # M5 bolt holes in base (2x for T-slot)
    bracket = bracket.faces("<Z").workplane().pushPoints([(0, -5), (0, 10)]).hole(BOLT_HOLE_D)

    # M3 holes in vertical face for rail mounting (2x)
    bracket = bracket.faces("<Y").workplane().pushPoints([(0, 10), (0, 30)]).hole(RAIL_MOUNT_HOLES)

    return bracket


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent / "stl" / "xz_gantry_frame.stl"
    svg = Path(__file__).parent.parent / "svg" / "xz_gantry_frame.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_xz_gantry_frame())
