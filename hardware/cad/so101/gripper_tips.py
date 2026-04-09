"""Compliant gripper fingertips — print in TPU 95A.

Adds soft grip surface to SO-101 stock gripper fingers.
Reference: https://www.thingiverse.com/thing:7153144 (NekoMaker TPU grip)

Usage:
    uv run --group cad python hardware/cad/so101/gripper_tips.py
"""

from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
# SO-101 gripper finger (approximate)
# TODO: measure from real hardware
FINGER_WIDTH = 20.0
FINGER_DEPTH = 8.0
TIP_THICKNESS = 3.0
TIP_LENGTH = 25.0

# Grip texture (ridges)
RIDGE_COUNT = 5
RIDGE_DEPTH = 0.8
RIDGE_WIDTH = 1.5


def build_gripper_tip() -> cq.Workplane:
    """Build one compliant gripper fingertip."""
    tip = cq.Workplane("XY").box(FINGER_WIDTH, TIP_THICKNESS, TIP_LENGTH)

    # Cut grip ridges on contact face
    for i in range(RIDGE_COUNT):
        z = -TIP_LENGTH / 2 + (i + 1) * TIP_LENGTH / (RIDGE_COUNT + 1)
        ridge = cq.Workplane("XY").box(FINGER_WIDTH + 1, RIDGE_DEPTH, RIDGE_WIDTH)
        ridge = ridge.translate((0, TIP_THICKNESS / 2 - RIDGE_DEPTH / 2, z))
        tip = tip.cut(ridge)

    return tip


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "gripper_tips_tpu.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "gripper_tips_tpu.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_gripper_tip())
