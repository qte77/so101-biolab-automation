"""Pipette tip rack holder — fixed workspace position.

Holds a standard 96-tip rack (SBS footprint variant).

Usage:
    uv run --group cad python hardware/cad/labware/tip_rack_holder.py
"""

from pathlib import Path

from build123d import Box, ExportSVG, Pos, export_stl

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


def build_tip_rack_holder():
    """Build tip rack holder tray."""
    base = Box(OUTER_L, OUTER_W, BASE_THICKNESS)

    walls = Pos(0, 0, BASE_THICKNESS / 2 + WALL_HEIGHT / 2) * Box(OUTER_L, OUTER_W, WALL_HEIGHT)
    inner = Pos(0, 0, BASE_THICKNESS / 2 + WALL_HEIGHT / 2) * Box(INNER_L, INNER_W, WALL_HEIGHT + 1)
    walls = walls - inner

    return base + walls


def export(part) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "labware" / "tip_rack_holder.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "labware" / "tip_rack_holder.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_tip_rack_holder())
