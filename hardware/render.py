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
        if "cad" not in part or "build_func" not in part:
            print(f"  SKIP {part['name']} — no CadQuery script")
            continue
        cad_rel = part["cad"]
        if cad_rel not in _modules:
            _modules[cad_rel] = _load_module(HARDWARE_DIR / cad_rel)

        mod = _modules[cad_rel]
        build_fn = getattr(mod, part["build_func"])
        shape = build_fn()

        stl_out = STL_DIR / part["stl"]
        svg_out = SVG_DIR / part["svg"]
        stl_out.parent.mkdir(parents=True, exist_ok=True)
        svg_out.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(shape, str(stl_out))
        cq.exporters.export(shape, str(svg_out), exportType="SVG")
        print(f"  {part['stl']} + {part['svg']}")


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

    # Generate SVGs from STLs (requires CadQuery for hidden-line removal)
    try:
        import cadquery  # noqa: F401
    except ImportError:
        print("--- SVG wireframe skipped (CadQuery not available)")
        return
    print("--- SVG wireframe from STLs")
    stl_to_svg = HARDWARE_DIR / "cad" / "util" / "stl_to_svg.py"
    subprocess.run([sys.executable, str(stl_to_svg), "--all"], check=True)


def run_theme() -> None:
    """Inject dark mode CSS into all SVGs."""
    theme_script = HARDWARE_DIR / "cad" / "util" / "theme_svgs.py"
    subprocess.run([sys.executable, str(theme_script)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render parts from manifest")
    parser.add_argument(
        "--backend", choices=["cad", "scad"], help="Force backend (default: auto-detect)"
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
        backend = force_backend or part.get("primary_backend", "cadquery")
        if backend in ("cad", "cadquery"):
            cad_parts.append(part)
        else:
            scad_parts.append(part)

    # Render each group with the appropriate backend
    if cad_parts:
        available = detect_backend()
        if available == "cad" or force_backend == "cad":
            render_cad(cad_parts)
        else:
            print(f"  CadQuery unavailable — falling back to OpenSCAD for {len(cad_parts)} parts")
            render_scad(cad_parts)

    if scad_parts:
        render_scad(scad_parts)

    run_theme()
    total = len(cad_parts) + len(scad_parts)
    print(f"=== {total} parts rendered (cad:{len(cad_parts)}, scad:{len(scad_parts)}) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
