"""96-well plate holder with alignment pins.

SBS/ANSI standard footprint: 127.76 × 85.48 mm.
Reference: https://en.wikipedia.org/wiki/Microplate#Standards

Usage:
    uv run --group cad python hardware/cad/labware/plate_holder.py

Exports:
    hardware/stl/labware/96well_plate_holder.stl
    hardware/svg/labware/96well_plate_holder.svg
"""

from pathlib import Path

from build123d import Box, Cylinder, Pos, export_stl, ExportSVG

# --- Parameters (all in mm) ---
# SBS standard plate footprint
PLATE_LENGTH = 127.76
PLATE_WIDTH = 85.48
PLATE_HEIGHT = 14.35  # Standard microplate height

# Holder dimensions
WALL_THICKNESS = 2.0
BASE_THICKNESS = 3.0
HOLDER_CLEARANCE = 0.5  # Gap between plate and holder walls
PIN_DIAMETER = 3.0
PIN_HEIGHT = 5.0
PIN_INSET = 5.0  # Distance from corner to pin center

# Derived
INNER_LENGTH = PLATE_LENGTH + HOLDER_CLEARANCE * 2
INNER_WIDTH = PLATE_WIDTH + HOLDER_CLEARANCE * 2
OUTER_LENGTH = INNER_LENGTH + WALL_THICKNESS * 2
OUTER_WIDTH = INNER_WIDTH + WALL_THICKNESS * 2
WALL_HEIGHT = PLATE_HEIGHT * 0.6  # Walls don't need to be full height


def build_plate_holder():
    """Build 96-well plate holder with alignment pins.

    Returns:
        build123d solid with the plate holder.
    """
    # Base plate
    holder = Pos(0, 0, BASE_THICKNESS / 2) * Box(OUTER_LENGTH, OUTER_WIDTH, BASE_THICKNESS)

    # Cut inner pocket for plate (leave 1mm floor)
    pocket_depth = BASE_THICKNESS - 1.0
    pocket = Pos(0, 0, BASE_THICKNESS - pocket_depth / 2) * Box(
        INNER_LENGTH, INNER_WIDTH, pocket_depth
    )
    holder = holder - pocket

    # Add walls
    walls = Pos(0, 0, BASE_THICKNESS + WALL_HEIGHT / 2) * Box(
        OUTER_LENGTH, OUTER_WIDTH, WALL_HEIGHT
    )
    inner_cut = Pos(0, 0, BASE_THICKNESS + WALL_HEIGHT / 2) * Box(
        INNER_LENGTH, INNER_WIDTH, WALL_HEIGHT + 1
    )
    walls = walls - inner_cut
    holder = holder + walls

    # Add alignment pins at corners
    pin_positions = [
        (INNER_LENGTH / 2 - PIN_INSET, INNER_WIDTH / 2 - PIN_INSET),
        (-INNER_LENGTH / 2 + PIN_INSET, INNER_WIDTH / 2 - PIN_INSET),
        (INNER_LENGTH / 2 - PIN_INSET, -INNER_WIDTH / 2 + PIN_INSET),
        (-INNER_LENGTH / 2 + PIN_INSET, -INNER_WIDTH / 2 + PIN_INSET),
    ]
    for x, y in pin_positions:
        pin = Pos(x, y, BASE_THICKNESS + PIN_HEIGHT / 2) * Cylinder(
            PIN_DIAMETER / 2, PIN_HEIGHT
        )
        holder = holder + pin

    return holder


def export(holder) -> None:
    """Export to STL and SVG."""
    stl_path = Path(__file__).parent.parent.parent / "stl" / "labware" / "96well_plate_holder.stl"
    svg_path = Path(__file__).parent.parent.parent / "svg" / "labware" / "96well_plate_holder.svg"

    export_stl(holder, str(stl_path))
    exporter = ExportSVG()
    exporter.add_shape(holder)
    exporter.write(str(svg_path))

    print(f"Exported: {stl_path}")
    print(f"Exported: {svg_path}")


if __name__ == "__main__":
    holder = build_plate_holder()
    export(holder)
