"""Assembly: pipette clamp + ejector lever + scanned dPette+ body.

Positions from user's 3D editor session — hand-aligned to match
the SO-101 wrist geometry.

Usage:
    uv run --group cad python hardware/cad/dpette/assembly_multi_focused.py
"""

import importlib.util
import math
from pathlib import Path

import cadquery as cq
import trimesh
import numpy as np

HARDWARE = Path(__file__).resolve().parent.parent.parent


def _load_cq(rel_path: str, func_name: str) -> cq.Workplane:
    full = HARDWARE / "cad" / rel_path
    spec = importlib.util.spec_from_file_location(full.stem, full)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)()


def _cq_to_trimesh(shape: cq.Workplane, tmp_name: str) -> trimesh.Trimesh:
    tmp = HARDWARE / "stl" / "dpette" / f"_tmp_{tmp_name}.stl"
    cq.exporters.export(shape, str(tmp))
    mesh = trimesh.load(str(tmp))
    tmp.unlink(missing_ok=True)
    return mesh


def _apply_transform(mesh: trimesh.Trimesh, pos: dict, rot_deg: dict) -> None:
    """Apply position + rotation (degrees) from the 3D editor export."""
    rx = math.radians(rot_deg["x"])
    ry = math.radians(rot_deg["y"])
    rz = math.radians(rot_deg["z"])
    # Build rotation matrix (Euler XYZ order, matching three.js default)
    rot = trimesh.transformations.euler_matrix(rx, ry, rz, axes='sxyz')
    rot[:3, 3] = [pos["x"], pos["y"], pos["z"]]
    mesh.apply_transform(rot)


def build_assembly() -> trimesh.Trimesh:
    """Assemble parts using user-provided editor positions."""

    clamp_mesh = _cq_to_trimesh(
        _load_cq("dpette/dpette_multi_handle.py", "build_dpette_multi_handle"), "clamp")
    lever_mesh = _cq_to_trimesh(
        _load_cq("dpette/dpette_multi_handle.py", "build_ejector_lever"), "lever")
    pip_mesh = trimesh.load(str(HARDWARE / "stl" / "dpette" / "0410_02_mesh.ply"))

    # Positions from user's 3D editor session (corrected)
    _apply_transform(clamp_mesh,
        pos={"x": 0, "y": 78.7, "z": 0},
        rot_deg={"x": -89.24, "y": 0, "z": 0})

    _apply_transform(lever_mesh,
        pos={"x": 0, "y": 80.49, "z": 36.37},
        rot_deg={"x": 89.58, "y": 3.97, "z": -179.97})

    _apply_transform(pip_mesh,
        pos={"x": 50.82, "y": -73.19, "z": -0.72},
        rot_deg={"x": -108.26, "y": -30.18, "z": 82.44})

    return trimesh.util.concatenate([clamp_mesh, lever_mesh, pip_mesh])


def main() -> None:
    assembly = build_assembly()

    stl_out = HARDWARE / "stl" / "dpette" / "assembly_multi_focused.stl"
    stl_out.parent.mkdir(parents=True, exist_ok=True)
    assembly.export(str(stl_out))
    print(f"Exported: {stl_out}")

    clamp_cq = _load_cq("dpette/dpette_multi_handle.py", "build_dpette_multi_handle")
    svg_out = HARDWARE / "svg" / "dpette" / "assembly_multi_focused.svg"
    svg_out.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(clamp_cq, str(svg_out), exportType="SVG")
    print(f"Exported: {svg_out}")


if __name__ == "__main__":
    main()
