"""96-well plate holder with alignment pins.

SBS/ANSI standard footprint: 127.76 × 85.48 mm.
Reference: https://en.wikipedia.org/wiki/Microplate#Standards

Usage:
    uv run --group cad python hardware/cad/plate_holder.py

Exports:
    hardware/stl/96well_plate_holder.stl
    hardware/svg/96well_plate_holder.svg
"""

from pathlib import Path

import cadquery as cq

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


def build_plate_holder() -> cq.Workplane:
    """Build 96-well plate holder with alignment pins.

    Returns:
        CadQuery workplane with the plate holder solid.
    """
    # Base plate
    holder = (
        cq.Workplane("XY")
        .box(OUTER_LENGTH, OUTER_WIDTH, BASE_THICKNESS)
        .translate((0, 0, BASE_THICKNESS / 2))
    )

    # Cut inner pocket for plate
    holder = (
        holder.faces(">Z")
        .workplane()
        .rect(INNER_LENGTH, INNER_WIDTH)
        .cutBlind(-BASE_THICKNESS + 1.0)  # Leave 1mm floor
    )

    # Add walls
    walls = (
        cq.Workplane("XY")
        .box(OUTER_LENGTH, OUTER_WIDTH, WALL_HEIGHT)
        .translate((0, 0, BASE_THICKNESS + WALL_HEIGHT / 2))
    )
    inner_cut = (
        cq.Workplane("XY")
        .box(INNER_LENGTH, INNER_WIDTH, WALL_HEIGHT + 1)
        .translate((0, 0, BASE_THICKNESS + WALL_HEIGHT / 2))
    )
    walls = walls.cut(inner_cut)
    holder = holder.union(walls)

    # Add alignment pins at corners
    pin_positions = [
        (INNER_LENGTH / 2 - PIN_INSET, INNER_WIDTH / 2 - PIN_INSET),
        (-INNER_LENGTH / 2 + PIN_INSET, INNER_WIDTH / 2 - PIN_INSET),
        (INNER_LENGTH / 2 - PIN_INSET, -INNER_WIDTH / 2 + PIN_INSET),
        (-INNER_LENGTH / 2 + PIN_INSET, -INNER_WIDTH / 2 + PIN_INSET),
    ]
    for x, y in pin_positions:
        pin = (
            cq.Workplane("XY")
            .cylinder(PIN_HEIGHT, PIN_DIAMETER / 2)
            .translate((x, y, BASE_THICKNESS + PIN_HEIGHT / 2))
        )
        holder = holder.union(pin)

    return holder


def export(holder: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl_path = Path(__file__).parent.parent / "stl" / "96well_plate_holder.stl"
    svg_path = Path(__file__).parent.parent / "svg" / "96well_plate_holder.svg"

    cq.exporters.export(holder, str(stl_path))
    cq.exporters.export(holder, str(svg_path), exportType="SVG")

    print(f"Exported: {stl_path}")
    print(f"Exported: {svg_path}")


if __name__ == "__main__":
    holder = build_plate_holder()
    export(holder)
