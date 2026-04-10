"""Exploded assembly: SO-101 wrist + tool changer + handle + dPette+.

Shows all arm-mounted parts in assembly order (top to bottom) with
gaps for clarity. Includes a simplified dPette+ body for context.

Usage:
    uv run --group cad python hardware/cad/assembly_so101_pipette.py
"""

import importlib.util
from pathlib import Path

import cadquery as cq

HARDWARE = Path(__file__).resolve().parent.parent


def _load(rel_path: str, func_name: str) -> cq.Workplane:
    """Import a CadQuery build function and call it."""
    full = HARDWARE / "cad" / rel_path
    spec = importlib.util.spec_from_file_location(full.stem, full)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)()


def _simplified_dpette() -> cq.Workplane:
    """Simplified dPette+ body: nozzle + barrel + tapered handle."""
    NOZZLE_R = 3.0
    NOZZLE_L = 30.0
    BARREL_R = 10.0
    BARREL_L = 40.0
    HANDLE_BOT_R = 11.0
    HANDLE_TOP_R = 16.0
    HANDLE_L = 80.0

    return (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .lineTo(NOZZLE_R, 0)
        .lineTo(NOZZLE_R, NOZZLE_L)
        .lineTo(BARREL_R, NOZZLE_L)
        .lineTo(HANDLE_BOT_R, NOZZLE_L + BARREL_L)
        .lineTo(HANDLE_TOP_R, NOZZLE_L + BARREL_L + HANDLE_L)
        .lineTo(0, NOZZLE_L + BARREL_L + HANDLE_L)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def build_assembly() -> "cq.Compound":
    """Build exploded assembly as a Compound (no boolean ops needed)."""
    # Load real parts
    robot_cone = _load("so101/tool_changer.py", "build_robot_cone")
    male_cone = _load("so101/tool_changer.py", "build_male_cone")
    handle = _load("dpette/dpette_handle.py", "build_mount_bracket")
    cam_arm = _load("dpette/dpette_handle.py", "build_cam_arm")
    dpette = _simplified_dpette()

    # Exploded positions (Z-up, 25 mm gaps between parts)
    GAP = 25.0
    shapes = []

    # 1. Robot cone (female, on SO-101 wrist) — topmost
    z = 220.0
    shapes.append(robot_cone.translate((0, 0, z)).val())

    # 2. Male cone (pipette tool-side) — mates into robot cone
    z -= GAP + 20.0
    shapes.append(male_cone.translate((0, 0, z)).val())

    # 3. Cam arm (on gripper horn) — offset to side for visibility
    z -= GAP + 5.0
    shapes.append(cam_arm.translate((30, 0, z)).val())

    # 4. Handle adapter — bolted to male cone base
    z -= GAP + 5.0
    shapes.append(handle.translate((0, 0, z)).val())

    # 5. dPette+ body (simplified) — inside handle
    z -= GAP + 80.0
    shapes.append(dpette.translate((0, 0, z)).val())

    return cq.Compound.makeCompound(shapes)


def main() -> None:
    compound = build_assembly()

    stl_out = HARDWARE / "stl" / "so101" / "assembly_so101_pipette.stl"
    svg_out = HARDWARE / "svg" / "so101" / "assembly_so101_pipette.svg"
    stl_out.parent.mkdir(parents=True, exist_ok=True)
    svg_out.parent.mkdir(parents=True, exist_ok=True)

    cq.exporters.export(compound, str(stl_out))
    cq.exporters.export(compound, str(svg_out), exportType="SVG")
    print(f"Exported: {stl_out}")
    print(f"Exported: {svg_out}")


if __name__ == "__main__":
    main()
