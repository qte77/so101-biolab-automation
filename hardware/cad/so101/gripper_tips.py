"""Compliant gripper fingertips — print in TPU 95A.

Adds soft grip surface to SO-101 stock gripper fingers.
Reference: https://www.thingiverse.com/thing:7153144 (NekoMaker TPU grip)

Usage:
    uv run --group cad python hardware/cad/so101/gripper_tips.py
"""

from pathlib import Path

from build123d import Box, ExportSVG, Pos, export_stl

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


def build_gripper_tip():
    """Build one compliant gripper fingertip."""
    tip = Box(FINGER_WIDTH, TIP_THICKNESS, TIP_LENGTH)

    # Cut grip ridges on contact face
    for i in range(RIDGE_COUNT):
        z = -TIP_LENGTH / 2 + (i + 1) * TIP_LENGTH / (RIDGE_COUNT + 1)
        ridge = Box(FINGER_WIDTH + 1, RIDGE_DEPTH, RIDGE_WIDTH)
        ridge = Pos(0, TIP_THICKNESS / 2 - RIDGE_DEPTH / 2, z) * ridge
        tip = tip - ridge

    return tip


def export(part) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent.parent / "stl" / "so101" / "gripper_tips_tpu.stl"
    svg = Path(__file__).parent.parent.parent / "svg" / "so101" / "gripper_tips_tpu.svg"
    export_stl(part, str(stl))
    exporter = ExportSVG()
    exporter.add_shape(part)
    exporter.write(str(svg))
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_gripper_tip())
