"""Fridge hook end-effector.

Attaches to the male tool cone base. Hook geometry designed
for standard lab fridge door handles (~20mm diameter bar).

Usage:
    uv run --group cad python hardware/cad/so101/fridge_hook.py

Exports:
    hardware/stl/so101/fridge_hook_tool.stl
    hardware/svg/so101/fridge_hook_tool.svg
"""

# Shared export helper (standalone mode)
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos

sys.path.append(str(Path(__file__).resolve().parent.parent))
from util.export import export_part

sys.path.pop()

# --- Parameters (all in mm) ---
# Hook geometry
HOOK_OPENING = 25.0  # Must fit around door handle (~20mm bar)
HOOK_DEPTH = 40.0  # How far the hook reaches
HOOK_THICKNESS = 6.0
HOOK_WIDTH = 20.0

# Mounting plate (mates with male tool cone base)
MOUNT_DIAMETER = 30.0  # Match tool cone top diameter
MOUNT_THICKNESS = 5.0


def build_fridge_hook():
    """Build fridge hook end-effector.

    Returns:
        build123d solid with hook.
    """
    # Mounting plate
    mount = Cylinder(MOUNT_DIAMETER / 2, MOUNT_THICKNESS)

    # Hook arm (vertical part)
    arm = Pos(0, 0, MOUNT_THICKNESS / 2 + HOOK_DEPTH / 2) * Box(
        HOOK_WIDTH, HOOK_THICKNESS, HOOK_DEPTH
    )

    # Hook tip (horizontal part curving inward)
    tip = Pos(
        0,
        -HOOK_OPENING / 2 + HOOK_THICKNESS / 2,
        MOUNT_THICKNESS / 2 + HOOK_DEPTH - HOOK_THICKNESS / 2,
    ) * Box(HOOK_WIDTH, HOOK_OPENING, HOOK_THICKNESS)

    return mount + arm + tip


def export(hook) -> None:
    """Export to STL and SVG."""
    export_part(hook, "so101", "fridge_hook_tool")


if __name__ == "__main__":
    hook = build_fridge_hook()
    export(hook)
