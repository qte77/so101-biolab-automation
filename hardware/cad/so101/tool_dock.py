"""3-station tool parking dock.

Holds 3 tools side-by-side with magnet retention.
Reference: Berkeley passive tool changer parking housing.

Usage:
    uv run --group cad python hardware/cad/so101/tool_dock.py
"""

from pathlib import Path

from build123d import Box, Cylinder, ExportSVG, Pos, export_stl

# --- Parameters (all in mm) ---
SLOT_DIAMETER = 38.0  # Fits tool cone base (36mm + clearance)
SLOT_DEPTH = 20.0
SLOT_SPACING = 50.0  # Center-to-center
NUM_SLOTS = 3
BASE_THICKNESS = 5.0
MAGNET_DIAMETER = 5.0
MAGNET_DEPTH = 3.0

DOCK_LENGTH = SLOT_SPACING * (NUM_SLOTS - 1) + SLOT_DIAMETER + 10
DOCK_WIDTH = SLOT_DIAMETER + 10


def build_tool_dock():
    """Build 3-station tool parking dock."""
    base = Box(DOCK_LENGTH, DOCK_WIDTH, BASE_THICKNESS + SLOT_DEPTH)

    for i in range(NUM_SLOTS):
        x = (i - 1) * SLOT_SPACING
        slot = Pos(x, 0, BASE_THICKNESS / 2) * Cylinder(SLOT_DIAMETER / 2, SLOT_DEPTH)
        base = base - slot

        # Magnet pocket at bottom of each slot
        z = -(BASE_THICKNESS + SLOT_DEPTH) / 2 + MAGNET_DEPTH / 2
        mag = Pos(x, 0, z) * Cylinder(MAGNET_DIAMETER / 2, MAGNET_DEPTH)
        base = base - mag

    return base


def export(part) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "so101" / "tool_dock_3station.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "so101" / "tool_dock_3station.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_tool_dock())
