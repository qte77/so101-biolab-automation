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

from pathlib import Path

import cadquery as cq

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


def build_pipette_mount() -> cq.Workplane:
    """Build dPette barrel clamp with tool cone mounting plate."""
    # Mounting plate (bolts to tool cone male base)
    mount = cq.Workplane("XY").box(MOUNT_WIDTH, MOUNT_WIDTH, MOUNT_THICKNESS)

    # Clamp body (cylinder around pipette barrel)
    clamp = (
        cq.Workplane("XY")
        .cylinder(CLAMP_LENGTH, CLAMP_OUTER / 2)
        .translate((0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH / 2))
    )

    # Cut barrel hole
    barrel = (
        cq.Workplane("XY")
        .cylinder(CLAMP_LENGTH + 1, (BARREL_DIAMETER + BARREL_CLEARANCE * 2) / 2)
        .translate((0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH / 2))
    )
    clamp = clamp.cut(barrel)

    # Cut split gap for clamping
    gap = (
        cq.Workplane("XY")
        .box(SPLIT_GAP, CLAMP_OUTER + 1, CLAMP_LENGTH + 1)
        .translate((0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH / 2))
    )
    clamp = clamp.cut(gap)

    # Ejector button cutout at top of clamp
    button_cut = (
        cq.Workplane("XY")
        .box(BUTTON_CUTOUT_WIDTH, BUTTON_CUTOUT_DEPTH, CLAMP_LENGTH * 0.4)
        .translate((0, 0, MOUNT_THICKNESS / 2 + CLAMP_LENGTH * 0.8))
    )
    clamp = clamp.cut(button_cut)

    # Screw holes for clamp tightening (2x M3)
    for z_off in [CLAMP_LENGTH * 0.25, CLAMP_LENGTH * 0.65]:
        hole = (
            cq.Workplane("XY")
            .cylinder(CLAMP_OUTER + 10, SCREW_DIAMETER / 2)
            .rotateAboutCenter((1, 0, 0), 90)
            .translate((0, 0, MOUNT_THICKNESS / 2 + z_off))
        )
        clamp = clamp.cut(hole)

    return mount.union(clamp)


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl_path = Path(__file__).parent.parent.parent / "stl" / "pipette_mount_so101.stl"
    svg_path = Path(__file__).parent.parent.parent / "svg" / "pipette_mount_so101.svg"
    cq.exporters.export(part, str(stl_path))
    cq.exporters.export(part, str(svg_path), exportType="SVG")
    print(f"Exported: {stl_path}")
    print(f"Exported: {svg_path}")


if __name__ == "__main__":
    export(build_pipette_mount())
