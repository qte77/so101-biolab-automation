"""Convert STL files to isometric wireframe SVGs using CadQuery.

CadQuery's SVG exporter renders visible edges with hidden-line removal,
producing proper 3D wireframe views — unlike OpenSCAD's projection()
which only gives silhouette outlines.

Usage:
    python hardware/cad/stl_to_svg.py hardware/stl/plate_holder.stl hardware/svg/plate_holder.svg
    python hardware/cad/stl_to_svg.py --all  # convert all STLs in hardware/stl/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

STL_DIR = Path(__file__).resolve().parent.parent / "stl"
SVG_DIR = Path(__file__).resolve().parent.parent / "svg"


def stl_to_svg(stl_path: Path, svg_path: Path) -> None:
    """Import STL and export as isometric wireframe SVG."""
    import cadquery as cq
    from OCP.StlAPI import StlAPI_Reader
    from OCP.TopoDS import TopoDS_Shape

    reader = StlAPI_Reader()
    ocp_shape = TopoDS_Shape()
    reader.Read(ocp_shape, str(stl_path))

    shape = cq.Workplane("XY").add(cq.Shape(ocp_shape))
    cq.exporters.export(shape, str(svg_path), exportType="SVG")
    print(f"  {svg_path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="STL → wireframe SVG via CadQuery")
    parser.add_argument("stl", nargs="?", help="Input STL file")
    parser.add_argument("svg", nargs="?", help="Output SVG file")
    parser.add_argument("--all", action="store_true", help="Convert all STLs")
    args = parser.parse_args()

    if args.all:
        stls = sorted(STL_DIR.glob("*.stl"))
        if not stls:
            print(f"No STL files in {STL_DIR}")
            return 1
        for stl in stls:
            svg = SVG_DIR / f"{stl.stem}.svg"
            stl_to_svg(stl, svg)
        return 0

    if args.stl and args.svg:
        stl_to_svg(Path(args.stl), Path(args.svg))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
