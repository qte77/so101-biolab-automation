"""Shared export helpers for CAD part files.

Centralizes STL + SVG export to avoid duplication across part scripts.
"""

from __future__ import annotations

from pathlib import Path

HARDWARE_DIR = Path(__file__).resolve().parent.parent.parent
STL_DIR = HARDWARE_DIR / "stl"
SVG_DIR = HARDWARE_DIR / "svg"


def export_part(part, subdir: str, filename: str) -> None:
    """Export a build123d shape to STL and isometric wireframe SVG.

    Args:
        part: build123d Solid/Compound.
        subdir: output subdirectory (e.g. "so101", "dpette", "labware").
        filename: stem without extension (e.g. "pipette_mount_so101").
    """
    from build123d import ExportSVG, Rot, export_stl

    stl_path = STL_DIR / subdir / f"{filename}.stl"
    svg_path = SVG_DIR / subdir / f"{filename}.svg"
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)

    export_stl(part, str(stl_path))

    try:
        iso = Rot(35.264, 0, -45) * part
        exporter = ExportSVG()
        exporter.add_shape(iso)
        exporter.write(str(svg_path))
    except Exception as exc:
        print(f"  SVG failed for {filename}: {exc}")

    print(f"Exported: {stl_path}")
