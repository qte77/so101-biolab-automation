"""XZ gantry Z-axis carriage with magnetic pipette dock.

Rides on MGN12 linear rail. Holds pipette via magnetic quick-swap dock
(2x 5mm neodymium magnets). Spring clip for security.

Generated with build123d.

Usage:
    uv run --group cad python hardware/cad/deferred/xz_carriage.py
"""

from pathlib import Path

from build123d import Box, Cylinder, ExportSVG, Pos, Rot, Solid, export_stl

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


def build_xz_carriage() -> Solid:
    """Build Z-axis carriage with pipette dock."""
    # Main body
    body = Box(CARRIAGE_W, CARRIAGE_D, CARRIAGE_H)

    # Rail mounting slot on top
    slot = Pos(0, 0, CARRIAGE_H / 2) * Box(RAIL_SLOT_W, RAIL_SLOT_D, WALL + 1)
    body = body - slot

    # Pipette bore (vertical through-hole from bottom)
    body = body - Cylinder(PIPETTE_BORE_D / 2, CARRIAGE_H + 1)

    # Magnet pockets (2x blind holes on front face)
    # The <Y face centroid is at (0, -CARRIAGE_D/2, 0).
    # pushPoints offsets (-10, 0) and (10, 0) are in face-local (X, Z) coords.
    # Blind holes go MAGNET_DEPTH into the face; position cylinder center at
    # Y = -CARRIAGE_D/2 + MAGNET_DEPTH/2 so it only cuts partway in.
    front_y = -CARRIAGE_D / 2 + MAGNET_DEPTH / 2
    for x_off in (-10, 10):
        body = body - Pos(x_off, front_y, 0) * Rot(90, 0, 0) * Cylinder(MAGNET_D / 2, MAGNET_DEPTH)

    return body


def export(part: Solid) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "deferred" / "xz_carriage_pipette_dock.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "deferred" / "xz_carriage_pipette_dock.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_xz_carriage())
