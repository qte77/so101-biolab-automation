"""Tip ejector station for dPette+ — universal single/multi-channel.

L-bracket with a horizontal finger that presses the side-mounted tip
ejector lever. Wide waste slot fits both single-channel and 8-channel
tip ejection. Robot moves pipette laterally into the finger.

Usage:
    uv run --group cad python hardware/cad/dpette/dpette_tip_release.py
"""

from pathlib import Path

import cadquery as cq

# --- Contact finger ---
FINGER_WIDTH = 12.0
FINGER_DEPTH = 15.0
FINGER_THICK = 5.0

# --- Vertical arm ---
ARM_HEIGHT = 75.0
ARM_WIDTH = 20.0
ARM_THICK = 6.0

# --- Base plate ---
BASE_X = 100.0
BASE_Y = 45.0
BASE_Z = 5.0

# --- Waste slot (wide enough for 8 tips @ 9 mm pitch) ---
WASTE_SLOT_W = 80.0
WASTE_SLOT_D = 18.0

# --- Mounting (4× M4) ---
M4_CLEARANCE = 4.2
BOLT_SPACING_X = 80.0
BOLT_SPACING_Y = 28.0


def build_tip_release() -> cq.Workplane:
    """L-bracket: base + arm + finger. Tips fall through waste slot."""
    # Base
    base = cq.Workplane("XY").box(BASE_X, BASE_Y, BASE_Z)
    base = base.cut(cq.Workplane("XY").box(WASTE_SLOT_W, WASTE_SLOT_D, BASE_Z + 2))
    base = (
        base.faces("<Z").workplane()
        .pushPoints([
            (-BOLT_SPACING_X / 2, -BOLT_SPACING_Y / 2),
            (BOLT_SPACING_X / 2, -BOLT_SPACING_Y / 2),
            (-BOLT_SPACING_X / 2, BOLT_SPACING_Y / 2),
            (BOLT_SPACING_X / 2, BOLT_SPACING_Y / 2),
        ])
        .hole(M4_CLEARANCE)
    )

    # Arm
    arm = cq.Workplane("XY").box(ARM_WIDTH, ARM_THICK, ARM_HEIGHT)
    arm_y = -BASE_Y / 2 + ARM_THICK / 2
    arm = arm.translate((0, arm_y, BASE_Z / 2 + ARM_HEIGHT / 2))

    # Finger
    finger = cq.Workplane("XY").box(FINGER_WIDTH, FINGER_DEPTH, FINGER_THICK)
    finger_y = arm_y + ARM_THICK / 2 + FINGER_DEPTH / 2
    finger_z = BASE_Z / 2 + ARM_HEIGHT - FINGER_THICK / 2
    finger = finger.translate((0, finger_y, finger_z))

    return base.union(arm).union(finger)


def export(part: cq.Workplane) -> None:
    base = Path(__file__).parent.parent.parent
    stl = base / "stl" / "dpette" / "dpette_tip_release.stl"
    svg = base / "svg" / "dpette" / "dpette_tip_release.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_tip_release())
