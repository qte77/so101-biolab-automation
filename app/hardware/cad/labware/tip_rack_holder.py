"""Pipette tip rack holder — fixed workspace position.

Holds a standard 96-tip rack (SBS footprint variant).

Usage:
    uv run --group cad python hardware/cad/labware/tip_rack_holder.py
"""

# Shared export helper (standalone mode)
import sys
from pathlib import Path

from build123d import Box, Pos

sys.path.append(str(Path(__file__).resolve().parent.parent))
from util.export import export_part

sys.path.pop()

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
    export_part(part, "labware", "tip_rack_holder")


if __name__ == "__main__":
    export(build_tip_rack_holder())
