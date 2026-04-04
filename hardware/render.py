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


def render_cad(parts: list[dict]) -> None:
    """Render all parts via CadQuery — import each script's build function."""
    print("--- Rendering via CadQuery")

    # Group parts by cad script (tool_changer.py serves multiple parts)
    by_script: dict[str, list[dict]] = {}
    for part in parts:
        by_script.setdefault(part["cad"], []).append(part)

    for cad_rel, script_parts in by_script.items():
        cad_path = HARDWARE_DIR / cad_rel
        spec = importlib.util.spec_from_file_location(cad_path.stem, cad_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Each CadQuery script has build_*() functions and an export_all() or export()
        # For simplicity, call the __main__ block via subprocess
        subprocess.run(
            [sys.executable, str(cad_path)],
            check=True,
        )
        # Mark all parts from this script as done
        for p in script_parts:
            print(f"  {p['stl']}")


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
