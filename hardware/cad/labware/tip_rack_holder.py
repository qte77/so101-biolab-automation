"""Pipette tip rack holder — fixed workspace position.

Holds a standard 96-tip rack (SBS footprint variant).

Usage:
    uv run --group cad python hardware/cad/labware/tip_rack_holder.py
"""

from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
# Standard tip rack (approximate — varies by manufacturer)
RACK_LENGTH = 122.0
RACK_WIDTH = 80.0
WALL_THICKNESS = 2.0
WALL_HEIGHT = 10.0
BASE_THICKNESS = 3.0
CLEARANCE = 0.5

INNER_L = RACK_LENGTH + CLEARANCE * 2
INNER_W = RACK_WIDTH + CLEARANCE * 2
OUTER_L = INNER_L + WALL_THICKNESS * 2
OUTER_W = INNER_W + WALL_THICKNESS * 2


def build_tip_rack_holder() -> cq.Workplane:
    """Build tip rack holder tray."""
    base = cq.Workplane("XY").box(OUTER_L, OUTER_W, BASE_THICKNESS)

    walls = cq.Workplane("XY").box(OUTER_L, OUTER_W, WALL_HEIGHT)
    walls = walls.translate((0, 0, BASE_THICKNESS / 2 + WALL_HEIGHT / 2))
    inner = cq.Workplane("XY").box(INNER_L, INNER_W, WALL_HEIGHT + 1)
    inner = inner.translate((0, 0, BASE_THICKNESS / 2 + WALL_HEIGHT / 2))
    walls = walls.cut(inner)

    return base.union(walls)


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "labware" / "tip_rack_holder.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "labware" / "tip_rack_holder.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_tip_rack_holder())
