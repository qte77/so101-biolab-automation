"""Pipette mount adapter — SO-101 wrist to dPette barrel.

Clamps around the dPette 7016 (single-channel) barrel and attaches to
the tool cone male base. The SO-101 arm holds the dPette as a tool,
moving it between positions.

Features a cutout at the top so the ejector button remains accessible
(for the tip ejection post or manual use).

Barrel dimensions are approximate — verify against real hardware.

Usage:
    uv run --group cad python hardware/cad/so101/pipette_mount.py
"""

# Shared export helper (standalone mode)
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot

sys.path.append(str(Path(__file__).resolve().parent.parent))
from util.export import export_part

sys.path.pop()

# --- Parameters (all in mm) ---
# dPette 7016 barrel (approximate — measure real hardware)
BARREL_DIAMETER = 20.0
BARREL_CLEARANCE = 0.3

# Clamp dimensions
CLAMP_LENGTH = 45.0  # Longer for stable grip
CLAMP_WALL = 4.0
CLAMP_OUTER = BARREL_DIAMETER + BARREL_CLEARANCE * 2 + CLAMP_WALL * 2

# Mounting plate (mates with tool cone male base)
MOUNT_WIDTH = 36.0
MOUNT_THICKNESS = 5.0

# Clamp split (for tightening around barrel)
SPLIT_GAP = 2.0
SCREW_DIAMETER = 3.2  # M3 clearance

# Ejector button clearance — cutout so top push-button stays accessible
BUTTON_CUTOUT_WIDTH = 12.0
BUTTON_CUTOUT_DEPTH = 8.0


def build_pipette_mount():
    """Build dPette barrel clamp with tool cone mounting plate."""
    # Mounting plate (bolts to tool cone male base)
    mount = Box(MOUNT_WIDTH, MOUNT_WIDTH, MOUNT_THICKNESS)

    # Clamp body (cylinder around pipette barrel)
    clamp = Pos(0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH / 2) * Cylinder(
        CLAMP_OUTER / 2, CLAMP_LENGTH
    )

    # Cut barrel hole
    barrel = Pos(0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH / 2) * Cylinder(
        (BARREL_DIAMETER + BARREL_CLEARANCE * 2) / 2, CLAMP_LENGTH + 1
    )
    clamp = clamp - barrel

    # Cut split gap for clamping
    gap = Pos(0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH / 2) * Box(
        SPLIT_GAP, CLAMP_OUTER + 1, CLAMP_LENGTH + 1
    )
    clamp = clamp - gap

    # Ejector button cutout at top of clamp
    button_cut = Pos(0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH * 0.8) * Box(
        BUTTON_CUTOUT_WIDTH, BUTTON_CUTOUT_DEPTH, CLAMP_LENGTH * 0.4
    )
    clamp = clamp - button_cut

    # Screw holes for clamp tightening (2x M3)
    for z_off in [CLAMP_LENGTH * 0.25, CLAMP_LENGTH * 0.65]:
        hole = (
            Pos(0, 0, MOUNT_THICKNESS / 2 + z_off)
            * Rot(90, 0, 0)
            * Cylinder(SCREW_DIAMETER / 2, CLAMP_OUTER + 10)
        )
        clamp = clamp - hole

    return mount + clamp


def export(part) -> None:
    """Export to STL and SVG."""
    export_part(part, "so101", "pipette_mount_so101")


if __name__ == "__main__":
    export(build_pipette_mount())
