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

from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
# SO-101 wrist flange (motor 5 horn mount)
# TODO: measure from real hardware or SO-ARM100 STEP files
WRIST_FLANGE_DIAMETER = 25.0  # Approximate
WRIST_SCREW_PATTERN_RADIUS = 9.0  # M3 screw circle radius
WRIST_SCREW_DIAMETER = 3.2  # M3 clearance

# Cone geometry (Berkeley design: 10° half-angle)
CONE_ANGLE_DEG = 10.0
CONE_HEIGHT = 15.0
CONE_TOP_DIAMETER = 30.0  # Wider end (mating surface)
CONE_BOTTOM_DIAMETER = CONE_TOP_DIAMETER - 2 * CONE_HEIGHT * 0.176  # tan(10°) ≈ 0.176

# Dowel pins for alignment
DOWEL_DIAMETER = 3.0
DOWEL_HEIGHT = 8.0
DOWEL_OFFSET = 10.0  # Distance from center

# Magnet pockets (5mm dia × 3mm deep neodymium)
MAGNET_DIAMETER = 5.0
MAGNET_DEPTH = 3.0
MAGNET_OFFSET = 12.0

# Base plate
BASE_THICKNESS = 5.0


def build_robot_cone() -> cq.Workplane:
    """Build female (robot-side) cone adapter for SO-101 wrist.

    Mounts to motor 5 horn via M3 screws. Has conical pocket
    that receives the male tool cone.

    Returns:
        CadQuery workplane with female cone solid.
    """
    # Base cylinder that mounts to wrist
    base = (
        cq.Workplane("XY")
        .cylinder(BASE_THICKNESS, CONE_TOP_DIAMETER / 2 + 3)
    )

    # Cut conical pocket (female)
    cone = (
        cq.Workplane("XY")
        .cone(CONE_HEIGHT, CONE_BOTTOM_DIAMETER / 2, CONE_TOP_DIAMETER / 2)
        .translate((0, 0, BASE_THICKNESS / 2))
    )
    base = base.cut(cone)

    # Cut M3 mounting holes for wrist flange
    import math

    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = WRIST_SCREW_PATTERN_RADIUS * math.cos(angle)
        y = WRIST_SCREW_PATTERN_RADIUS * math.sin(angle)
        hole = (
            cq.Workplane("XY")
            .cylinder(BASE_THICKNESS + 1, WRIST_SCREW_DIAMETER / 2)
            .translate((x, y, 0))
        )
        base = base.cut(hole)

    # Add dowel pin holes
    for sign in [1, -1]:
        hole = (
            cq.Workplane("XY")
            .cylinder(DOWEL_HEIGHT, DOWEL_DIAMETER / 2)
            .translate((sign * DOWEL_OFFSET, 0, -BASE_THICKNESS / 2 + DOWEL_HEIGHT / 2))
        )
        base = base.cut(hole)

    # Magnet pockets
    for sign in [1, -1]:
        pocket = (
            cq.Workplane("XY")
            .cylinder(MAGNET_DEPTH, MAGNET_DIAMETER / 2)
            .translate((0, sign * MAGNET_OFFSET, BASE_THICKNESS / 2 - MAGNET_DEPTH / 2))
        )
        base = base.cut(pocket)

    return base


def build_male_cone() -> cq.Workplane:
    """Build male (tool-side) cone base.

    Shared by all tools (pipette, gripper, hook). Each tool attaches
    to the flat back of this cone.

    Returns:
        CadQuery workplane with male cone solid.
    """
    # Conical protrusion (male)
    cone = (
        cq.Workplane("XY")
        .cone(CONE_HEIGHT, CONE_BOTTOM_DIAMETER / 2 - 0.3, CONE_TOP_DIAMETER / 2 - 0.3)
    )

    # Base plate for tool attachment
    base = (
        cq.Workplane("XY")
        .cylinder(BASE_THICKNESS, CONE_TOP_DIAMETER / 2 + 3)
        .translate((0, 0, -CONE_HEIGHT / 2 - BASE_THICKNESS / 2))
    )

    result = cone.union(base)

    # Dowel pin protrusions
    for sign in [1, -1]:
        pin = (
            cq.Workplane("XY")
            .cylinder(DOWEL_HEIGHT, DOWEL_DIAMETER / 2 - 0.1)
            .translate((sign * DOWEL_OFFSET, 0, CONE_HEIGHT / 2 + DOWEL_HEIGHT / 2))
        )
        result = result.union(pin)

    # Magnet pockets (matching robot side)
    for sign in [1, -1]:
        pocket = (
            cq.Workplane("XY")
            .cylinder(MAGNET_DEPTH, MAGNET_DIAMETER / 2)
            .translate(
                (0, sign * MAGNET_OFFSET, CONE_HEIGHT / 2 - MAGNET_DEPTH / 2)
            )
        )
        result = result.cut(pocket)

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
