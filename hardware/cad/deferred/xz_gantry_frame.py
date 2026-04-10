"""XZ gantry bridge frame — bracket pair for 2020 aluminium extrusion.

Spans mini cooler to PCR block (~300mm). Two identical brackets hold
the X-axis rail. Designed for M5 T-slot bolts.

Generated with build123d.

Usage:
    uv run --group cad python hardware/cad/deferred/xz_gantry_frame.py
"""

from pathlib import Path

from build123d import Box, Cylinder, ExportSVG, Pos, Rot, Solid, export_stl

# --- Parameters (all in mm) ---
BRACKET_WIDTH = 40.0
BRACKET_HEIGHT = 60.0
BRACKET_DEPTH = 30.0
WALL = 4.0
EXTRUSION_SLOT = 20.0  # 2020 profile
BOLT_HOLE_D = 5.2  # M5 clearance
RAIL_MOUNT_HOLES = 3.2  # M3 for MGN12 rail


def build_xz_gantry_frame() -> Solid:
    """Build one L-bracket for XZ gantry frame."""
    # Horizontal base (bolts to extrusion or table)
    base = Box(BRACKET_WIDTH, BRACKET_DEPTH, WALL)

    # Vertical plate (holds rail)
    vertical = Pos(0, -BRACKET_DEPTH / 2 + WALL / 2, BRACKET_HEIGHT / 2) * Box(
        BRACKET_WIDTH, WALL, BRACKET_HEIGHT
    )

    bracket = base + vertical

    # M5 bolt holes in base (2x for T-slot) — through-holes from bottom face
    for y_off in (-5, 10):
        bracket = bracket - Pos(0, y_off, 0) * Cylinder(BOLT_HOLE_D / 2, WALL + 1)

    # M3 holes in vertical face for rail mounting (2x) — horizontal through-holes
    # The vertical plate back face (<Y) centroid is at
    # (0, -BRACKET_DEPTH/2 + WALL/2, BRACKET_HEIGHT/2).
    # pushPoints offsets (0, 10) and (0, 30) are in face-local (X, Z) coords,
    # so Z_absolute = BRACKET_HEIGHT/2 + offset.
    vert_y = -BRACKET_DEPTH / 2 + WALL / 2
    vert_z_center = BRACKET_HEIGHT / 2
    for z_off in (10, 30):
        bracket = bracket - Pos(0, vert_y, vert_z_center + z_off) * Rot(90, 0, 0) * Cylinder(
            RAIL_MOUNT_HOLES / 2, WALL + 1
        )

    return bracket


def export(part: Solid) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "deferred" / "xz_gantry_frame.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "deferred" / "xz_gantry_frame.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_xz_gantry_frame())
