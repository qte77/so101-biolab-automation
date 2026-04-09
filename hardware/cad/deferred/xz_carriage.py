"""XZ gantry Z-axis carriage with magnetic pipette dock.

Rides on MGN12 linear rail. Holds pipette via magnetic quick-swap dock
(2x 5mm neodymium magnets). Spring clip for security.

Usage:
    uv run --group cad python hardware/cad/deferred/xz_carriage.py
"""

from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
CARRIAGE_W = 50.0
CARRIAGE_H = 40.0
CARRIAGE_D = 30.0
WALL = 3.0
RAIL_SLOT_W = 13.0  # MGN12 carriage width
RAIL_SLOT_D = 8.0
MAGNET_D = 5.0
MAGNET_DEPTH = 3.0
PIPETTE_BORE_D = 22.0  # Fits dPette 7016 barrel


def build_xz_carriage() -> cq.Workplane:
    """Build Z-axis carriage with pipette dock."""
    # Main body
    body = cq.Workplane("XY").box(CARRIAGE_W, CARRIAGE_D, CARRIAGE_H)

    # Rail mounting slot on top
    slot = cq.Workplane("XY").box(RAIL_SLOT_W, RAIL_SLOT_D, WALL + 1)
    slot = slot.translate((0, 0, CARRIAGE_H / 2))
    body = body.cut(slot)

    # Pipette bore (vertical through-hole)
    body = body.faces("<Z").workplane().hole(PIPETTE_BORE_D)

    # Magnet pockets (2x on front face)
    body = body.faces("<Y").workplane().pushPoints([(-10, 0), (10, 0)]).hole(MAGNET_D, MAGNET_DEPTH)

    return body


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "xz_carriage_pipette_dock.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "xz_carriage_pipette_dock.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_xz_carriage())
