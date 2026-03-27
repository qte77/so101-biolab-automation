"""Tool changer components — robot-side and tool-side cones.

Based on Berkeley AutoLab passive modular tool changer design:
- Paper: https://goldberg.berkeley.edu/pubs/CASE2018-ron-tool-changer-submitted.pdf
- Repo: https://github.com/BerkeleyAutomation/RobotToolChanger

Key design: truncated cone (10° angle) + dowel pin alignment.

Usage:
    uv run --group cad python hardware/cad/tool_changer.py

Exports:
    hardware/stl/tool_cone_robot.stl   (female, mounts on SO-101 wrist)
    hardware/stl/tool_cone_pipette.stl (male, attaches to pipette)
    hardware/stl/tool_cone_gripper.stl (male, attaches to gripper)
    hardware/stl/tool_cone_hook.stl    (male, attaches to fridge hook)
    hardware/svg/tool_cone_robot.svg
    hardware/svg/tool_cone_male.svg
"""

import math
from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
# SO-101 wrist flange (motor 5 horn mount)
# TODO: measure from real hardware or SO-ARM100 STEP files
WRIST_SCREW_PATTERN_RADIUS = 9.0
WRIST_SCREW_DIAMETER = 3.2  # M3 clearance

# Cone geometry (Berkeley design: 10° half-angle)
CONE_ANGLE_DEG = 10.0
CONE_HEIGHT = 15.0
CONE_TOP_RADIUS = 15.0
CONE_BOTTOM_RADIUS = CONE_TOP_RADIUS - CONE_HEIGHT * math.tan(math.radians(CONE_ANGLE_DEG))

# Dowel pins for alignment
DOWEL_DIAMETER = 3.0
DOWEL_HEIGHT = 8.0
DOWEL_OFFSET = 10.0

# Magnet pockets (5mm dia × 3mm deep neodymium)
MAGNET_DIAMETER = 5.0
MAGNET_DEPTH = 3.0
MAGNET_OFFSET = 12.0

# Base plate
BASE_THICKNESS = 5.0
BASE_RADIUS = CONE_TOP_RADIUS + 3


def _make_truncated_cone(height: float, r_bottom: float, r_top: float) -> cq.Workplane:
    """Create a truncated cone (frustum) via revolve.

    Args:
        height: Cone height.
        r_bottom: Bottom radius (smaller).
        r_top: Top radius (larger).

    Returns:
        CadQuery solid.
    """
    return (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .lineTo(r_bottom, 0)
        .lineTo(r_top, height)
        .lineTo(0, height)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def build_robot_cone() -> cq.Workplane:
    """Build female (robot-side) cone adapter for SO-101 wrist.

    Returns:
        CadQuery workplane with female cone solid.
    """
    # Base cylinder
    base = cq.Workplane("XY").cylinder(BASE_THICKNESS, BASE_RADIUS)

    # Cut conical pocket (female)
    cone = _make_truncated_cone(CONE_HEIGHT, CONE_BOTTOM_RADIUS, CONE_TOP_RADIUS)
    cone = cone.translate((0, 0, -BASE_THICKNESS / 2 + 0.5))
    base = base.cut(cone)

    # M3 mounting holes (4x at 90° intervals, offset 45°)
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = WRIST_SCREW_PATTERN_RADIUS * math.cos(angle)
        y = WRIST_SCREW_PATTERN_RADIUS * math.sin(angle)
        hole = cq.Workplane("XY").cylinder(BASE_THICKNESS + 1, WRIST_SCREW_DIAMETER / 2)
        base = base.cut(hole.translate((x, y, 0)))

    # Dowel pin holes (2x, opposing)
    for sign in [1, -1]:
        hole = cq.Workplane("XY").cylinder(DOWEL_HEIGHT, DOWEL_DIAMETER / 2)
        base = base.cut(hole.translate((sign * DOWEL_OFFSET, 0, BASE_THICKNESS / 2 - DOWEL_HEIGHT / 2)))

    # Magnet pockets (2x, opposing on Y axis)
    for sign in [1, -1]:
        pocket = cq.Workplane("XY").cylinder(MAGNET_DEPTH, MAGNET_DIAMETER / 2)
        base = base.cut(pocket.translate((0, sign * MAGNET_OFFSET, -BASE_THICKNESS / 2 + MAGNET_DEPTH / 2)))

    return base


def build_male_cone() -> cq.Workplane:
    """Build male (tool-side) cone base.

    Returns:
        CadQuery workplane with male cone solid.
    """
    # Conical protrusion (0.3mm smaller for clearance)
    cone = _make_truncated_cone(
        CONE_HEIGHT, CONE_BOTTOM_RADIUS - 0.3, CONE_TOP_RADIUS - 0.3
    )

    # Base plate for tool attachment
    base = cq.Workplane("XY").cylinder(BASE_THICKNESS, BASE_RADIUS)
    base = base.translate((0, 0, -CONE_HEIGHT / 2 - BASE_THICKNESS / 2))

    result = cone.union(base)

    # Dowel pin protrusions (0.1mm smaller for fit)
    for sign in [1, -1]:
        pin = cq.Workplane("XY").cylinder(DOWEL_HEIGHT, DOWEL_DIAMETER / 2 - 0.1)
        result = result.union(pin.translate((sign * DOWEL_OFFSET, 0, CONE_HEIGHT / 2 + DOWEL_HEIGHT / 2)))

    # Magnet pockets (matching robot side)
    for sign in [1, -1]:
        pocket = cq.Workplane("XY").cylinder(MAGNET_DEPTH, MAGNET_DIAMETER / 2)
        result = result.cut(pocket.translate((0, sign * MAGNET_OFFSET, CONE_HEIGHT / 2 - MAGNET_DEPTH / 2)))

    return result


def export_all() -> None:
    """Export all tool changer components."""
    stl_dir = Path(__file__).parent.parent / "stl"
    svg_dir = Path(__file__).parent.parent / "svg"

    robot_cone = build_robot_cone()
    cq.exporters.export(robot_cone, str(stl_dir / "tool_cone_robot.stl"))
    cq.exporters.export(robot_cone, str(svg_dir / "tool_cone_robot.svg"), exportType="SVG")
    print("Exported: tool_cone_robot.stl + .svg")

    male_cone = build_male_cone()
    for name in ["pipette", "gripper", "hook"]:
        cq.exporters.export(male_cone, str(stl_dir / f"tool_cone_{name}.stl"))
        print(f"Exported: tool_cone_{name}.stl")

    cq.exporters.export(male_cone, str(svg_dir / "tool_cone_male.svg"), exportType="SVG")
    print("Exported: tool_cone_male.svg")


if __name__ == "__main__":
    export_all()
