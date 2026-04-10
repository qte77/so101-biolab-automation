"""Exploded assembly: SO-101 arm + dPette+ 8-channel pipette.

Shows all arm-mounted parts for multi-channel pipetting in assembly
order (top to bottom) with gaps for clarity. Includes a simplified
8-channel dPette+ body for context.

Usage:
    uv run --group cad python hardware/cad/assembly_so101_multi.py
"""

import importlib.util
from pathlib import Path

import cadquery as cq

HARDWARE = Path(__file__).resolve().parent.parent


def _load(rel_path: str, func_name: str) -> cq.Workplane:
    full = HARDWARE / "cad" / rel_path
    spec = importlib.util.spec_from_file_location(full.stem, full)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)()


def _simplified_dpette_multi() -> cq.Workplane:
    """Simplified dPette+ 8-channel body: rectangular handle + 8 nozzles."""
    BODY_W = 50.0
    BODY_D = 25.0
    BODY_H = 70.0
    NOZZLE_R = 2.5
    NOZZLE_L = 35.0
    TIP_SPACING = 9.0

    # Main body
    body = cq.Workplane("XY").box(BODY_W, BODY_D, BODY_H)
    body = body.translate((0, 0, BODY_H / 2 + NOZZLE_L))

    # 8 nozzles
    for i in range(8):
        x = -3.5 * TIP_SPACING + i * TIP_SPACING
        nozzle = cq.Workplane("XY").circle(NOZZLE_R).extrude(NOZZLE_L)
        nozzle = nozzle.translate((x, 0, 0))
        body = body.union(nozzle)

    return body


def build_assembly() -> "cq.Compound":
    """Build exploded assembly as a Compound."""
    robot_cone = _load("so101/tool_changer.py", "build_robot_cone")
    male_cone = _load("so101/tool_changer.py", "build_male_cone")
    cam_arm = _load("dpette/dpette_handle.py", "build_cam_arm")
    handle = _load("dpette/dpette_multi_handle.py", "build_dpette_multi_handle")

    dpette = _simplified_dpette_multi()

    GAP = 25.0
    shapes = []

    z = 220.0
    shapes.append(robot_cone.translate((0, 0, z)).val())

    z -= GAP + 20.0
    shapes.append(male_cone.translate((0, 0, z)).val())

    z -= GAP + 5.0
    shapes.append(cam_arm.translate((40, 0, z)).val())

    z -= GAP + 5.0
    shapes.append(handle.translate((0, 0, z)).val())

    z -= GAP + 70.0
    shapes.append(dpette.translate((0, 0, z)).val())

    return cq.Compound.makeCompound(shapes)


def main() -> None:
    compound = build_assembly()

    stl_out = HARDWARE / "stl" / "so101" / "assembly_so101_multi.stl"
    svg_out = HARDWARE / "svg" / "so101" / "assembly_so101_multi.svg"
    stl_out.parent.mkdir(parents=True, exist_ok=True)
    svg_out.parent.mkdir(parents=True, exist_ok=True)

    cq.exporters.export(compound, str(stl_out))
    cq.exporters.export(compound, str(svg_out), exportType="SVG")
    print(f"Exported: {stl_out}")
    print(f"Exported: {svg_out}")


if __name__ == "__main__":
    main()
