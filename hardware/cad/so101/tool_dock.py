"""3-station tool parking dock.

Holds 3 tools side-by-side with magnet retention.
Reference: Berkeley passive tool changer parking housing.

Usage:
    uv run --group cad python hardware/cad/so101/tool_dock.py
"""

from pathlib import Path

import cadquery as cq

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


def build_tool_dock() -> cq.Workplane:
    """Build 3-station tool parking dock."""
    base = cq.Workplane("XY").box(DOCK_LENGTH, DOCK_WIDTH, BASE_THICKNESS + SLOT_DEPTH)

    for i in range(NUM_SLOTS):
        x = (i - 1) * SLOT_SPACING
        slot = cq.Workplane("XY").cylinder(SLOT_DEPTH, SLOT_DIAMETER / 2)
        slot = slot.translate((x, 0, BASE_THICKNESS / 2))
        base = base.cut(slot)

        # Magnet pocket at bottom of each slot
        mag = cq.Workplane("XY").cylinder(MAGNET_DEPTH, MAGNET_DIAMETER / 2)
        z = -(BASE_THICKNESS + SLOT_DEPTH) / 2 + MAGNET_DEPTH / 2
        base = base.cut(mag.translate((x, 0, z)))

    return base


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "so101" / "tool_dock_3station.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "so101" / "tool_dock_3station.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_tool_dock())
