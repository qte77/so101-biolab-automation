"""Render all parts from hardware/parts.json manifest.

Auto-detects backend: CadQuery (preferred) or OpenSCAD (fallback).
Runs theme_svgs.py after generation.

Usage:
    python hardware/render.py                # auto-detect
    python hardware/render.py --backend cad  # force CadQuery
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

HARDWARE_DIR = Path(__file__).resolve().parent
MANIFEST = HARDWARE_DIR / "parts.json"
STL_DIR = HARDWARE_DIR / "stl"
SVG_DIR = HARDWARE_DIR / "svg"


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST.read_text())


def detect_backend() -> str:
    """Return 'cad' if CadQuery importable, 'scad' if openscad binary found, else error."""
    try:
        import cadquery  # noqa: F401

        return "cad"
    except ImportError:
        pass
    if shutil.which("openscad"):
        return "scad"
    print("ERROR: Neither CadQuery nor OpenSCAD found")
    print("  Run: make setup_cad   (preferred)")
    print("  Or:  make setup_scad  (fallback)")
    sys.exit(1)


def _load_module(cad_path: Path):
    """Import a CadQuery script as a module."""
    spec = importlib.util.spec_from_file_location(cad_path.stem, cad_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render_cad(parts: list[dict]) -> None:
    """Render all parts via CadQuery — import build functions, export using manifest filenames."""
    import cadquery as cq

    print("--- Rendering via CadQuery")

    # Cache modules (tool_changer.py is used by multiple parts)
    _modules: dict[str, object] = {}

    for part in parts:
        cad_rel = part["cad"]
        if cad_rel not in _modules:
            _modules[cad_rel] = _load_module(HARDWARE_DIR / cad_rel)

        mod = _modules[cad_rel]
        build_fn = getattr(mod, part["build_func"])
        shape = build_fn()

        cq.exporters.export(shape, str(STL_DIR / part["stl"]))
        cq.exporters.export(shape, str(SVG_DIR / part["svg"]), exportType="SVG")
        print(f"  {part['stl']} + {part['svg']}")


def render_scad(parts: list[dict]) -> None:
    """Render all parts via OpenSCAD CLI, then generate SVGs."""
    print("--- Rendering via OpenSCAD (fallback)")

    for part in parts:
        scad_path = HARDWARE_DIR / part["scad"]
        stl_path = STL_DIR / part["stl"]
        args = part.get("scad_args", "").split()
        cmd = ["openscad", "-o", str(stl_path), *args, str(scad_path)]
        cmd = [c for c in cmd if c]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  {part['stl']}")

    # Generate SVGs from STLs (CadQuery's stl_to_svg.py)
    print("--- SVG wireframe from STLs")
    stl_to_svg = HARDWARE_DIR / "cad" / "stl_to_svg.py"
    subprocess.run([sys.executable, str(stl_to_svg), "--all"], check=True)


def run_theme() -> None:
    """Inject dark mode CSS into all SVGs."""
    theme_script = HARDWARE_DIR / "cad" / "theme_svgs.py"
    subprocess.run([sys.executable, str(theme_script)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render parts from manifest")
    parser.add_argument(
        "--backend", choices=["cad", "scad"], help="Force backend (default: auto-detect)"
    )
    args = parser.parse_args()

    backend = args.backend or detect_backend()
    parts = load_manifest()

    if backend == "cad":
        render_cad(parts)
    else:
        render_scad(parts)

    run_theme()
    print(f"=== {len(parts)} parts rendered via {backend} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
