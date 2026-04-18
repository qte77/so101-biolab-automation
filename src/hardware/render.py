"""Render all parts from hardware/parts.json manifest.

Auto-detects backend: build123d (preferred) or OpenSCAD (fallback).
SVGs default to wireframe; use --solid for filled faces.
Runs theme_svgs.py after generation.

Usage:
    python hardware/render.py                # wireframe SVG (default)
    python hardware/render.py --solid        # solid-filled SVG
    python hardware/render.py --backend cad  # force build123d
    python hardware/render.py --backend scad # force OpenSCAD
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import types

HARDWARE_DIR = Path(__file__).resolve().parent  # src/hardware/ — code
MANIFEST = HARDWARE_DIR / "parts.json"
ASSETS_DIR = (
    HARDWARE_DIR.parents[1] / "hardware"
)  # top-level hardware/ — generated + reference assets
STL_DIR = ASSETS_DIR / "stl"
SVG_DIR = ASSETS_DIR / "svg"

# Backend constants — normalize manifest values to these
BACKEND_CAD = "cad"
BACKEND_SCAD = "scad"
_CAD_ALIASES = frozenset({"cad", "cadquery", "build123d"})


def load_manifest() -> list[dict]:
    """Load the parts manifest from JSON."""
    return json.loads(MANIFEST.read_text())


def detect_backend() -> str:
    """Return BACKEND_CAD if build123d importable, BACKEND_SCAD if openscad found, else error."""
    try:
        import build123d  # noqa: F401  # pyright: ignore[reportMissingImports]

        return BACKEND_CAD
    except ImportError:
        pass
    if shutil.which("openscad"):
        return BACKEND_SCAD
    print("ERROR: Neither build123d nor OpenSCAD found")
    print("  Run: make setup_cad   (preferred)")
    print("  Or:  make setup_scad  (fallback)")
    sys.exit(1)


def _load_module(cad_path: Path) -> types.ModuleType:
    """Import a CAD script as a module."""
    spec = importlib.util.spec_from_file_location(cad_path.stem, cad_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load CAD module from {cad_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _to_solid(shape: Any) -> Any:  # noqa: ANN401
    """Coerce build123d result (Solid, Compound, or ShapeList) to exportable Shape."""
    from build123d import Compound, Solid  # pyright: ignore[reportMissingImports]

    if isinstance(shape, Solid):
        return shape
    if isinstance(shape, Compound):
        return shape
    # ShapeList or other iterable — wrap in Compound
    if hasattr(shape, "__iter__"):
        return Compound(children=list(shape))
    return shape


def render_cad(parts: list[dict], *, solid: bool = False) -> None:
    """Render all parts via build123d — import build functions, export using manifest filenames."""
    from build123d import (  # pyright: ignore[reportMissingImports]
        Color,
        ExportSVG,
        LineType,
        Rot,
        export_stl,
    )

    print("--- Rendering via build123d")

    # Cache modules and build results (tool_changer.py exports same shape 3x)
    _modules: dict[str, object] = {}
    _shapes: dict[tuple[str, str], object] = {}

    for part in parts:
        if "cad" not in part or "build_func" not in part:
            print(f"  SKIP {part['name']} — no CAD script")
            continue
        cad_rel = part["cad"]
        func_name = part["build_func"]
        cache_key = (cad_rel, func_name)

        if cache_key not in _shapes:
            if cad_rel not in _modules:
                _modules[cad_rel] = _load_module(HARDWARE_DIR / cad_rel)
            mod = _modules[cad_rel]
            _shapes[cache_key] = _to_solid(getattr(mod, func_name)())

        shape = _shapes[cache_key]

        stl_out = STL_DIR / part["stl"]
        svg_out = SVG_DIR / part["svg"]
        stl_out.parent.mkdir(parents=True, exist_ok=True)
        svg_out.parent.mkdir(parents=True, exist_ok=True)
        export_stl(shape, str(stl_out))
        try:
            # Rotate to isometric view (ExportSVG projects top-down on XY)
            iso_shape = Rot(35.264, 0, -45) * shape
            exporter = ExportSVG()
            if solid:
                exporter.add_layer(
                    "solid",
                    fill_color=Color(0.85, 0.85, 0.85),
                    line_color=Color(0, 0, 0),
                    line_weight=0.5,
                )
                exporter.add_layer(
                    "hidden",
                    line_color=Color(0.6, 0.6, 0.6),
                    line_weight=0.25,
                    line_type=LineType.ISO_DOT,
                )
                exporter.add_shape(iso_shape, layer="solid")
            else:
                exporter.add_shape(iso_shape)
            exporter.write(str(svg_out))
            print(f"  {part['stl']} + {part['svg']}")
        except Exception as exc:
            print(f"  {part['stl']} (SVG failed: {exc})")


def render_scad(parts: list[dict]) -> None:
    """Render all parts via OpenSCAD CLI, then generate SVGs."""
    print("--- Rendering via OpenSCAD (fallback)")

    for part in parts:
        if "scad" not in part:
            print(f"  SKIP {part['name']} — no .scad script")
            continue
        scad_path = HARDWARE_DIR / part["scad"]
        stl_path = STL_DIR / part["stl"]
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        args = part.get("scad_args", "").split()
        cmd = ["openscad", "-o", str(stl_path), *args, str(scad_path)]
        cmd = [c for c in cmd if c]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  {part['stl']}")

    # Generate SVGs from STLs (build123d's stl_to_svg.py)
    print("--- SVG wireframe from STLs")
    stl_to_svg = HARDWARE_DIR / "cad" / "util" / "stl_to_svg.py"
    subprocess.run([sys.executable, str(stl_to_svg), "--all"], check=True)


def run_theme() -> None:
    """Inject dark mode CSS into all SVGs."""
    theme_script = HARDWARE_DIR / "cad" / "util" / "theme_svgs.py"
    subprocess.run([sys.executable, str(theme_script)], check=True)


def main() -> int:
    """CLI entry point for rendering parts."""
    parser = argparse.ArgumentParser(description="Render parts from manifest")
    parser.add_argument(
        "--backend", choices=["cad", "scad"], help="Force backend (default: auto-detect)"
    )
    parser.add_argument(
        "--solid", action="store_true", help="Filled SVG faces (default: wireframe)"
    )
    args = parser.parse_args()

    force_backend = args.backend
    all_parts = load_manifest()

    # Skip deferred/planned parts
    parts = [p for p in all_parts if p.get("status") not in ("deferred", "planned")]
    skipped = len(all_parts) - len(parts)
    if skipped:
        print(f"--- Skipping {skipped} deferred/planned parts")

    # Split parts by primary_backend (or use forced backend)
    cad_parts = []
    scad_parts = []
    for part in parts:
        backend = force_backend or part.get("primary_backend", "build123d")
        if backend in _CAD_ALIASES:
            cad_parts.append(part)
        else:
            scad_parts.append(part)

    # Render each group with the appropriate backend
    if cad_parts:
        available = detect_backend()
        if available == BACKEND_CAD:
            render_cad(cad_parts, solid=args.solid)
        elif force_backend == BACKEND_CAD:
            print("ERROR: --backend cad requested but build123d not installed")
            sys.exit(1)
        else:
            print(f"  build123d unavailable — falling back to OpenSCAD for {len(cad_parts)} parts")
            render_scad(cad_parts)

    if scad_parts:
        render_scad(scad_parts)

    run_theme()
    total = len(cad_parts) + len(scad_parts)
    print(f"=== {total} parts rendered (cad:{len(cad_parts)}, scad:{len(scad_parts)}) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
