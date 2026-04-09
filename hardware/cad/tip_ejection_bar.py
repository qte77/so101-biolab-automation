"""Tip ejection bar — fixed bracket for mechanical tip removal.

Mounted at the waste position. The pipette's tip ejector lever presses
against this bar to pop off used tips. Works with both XZ gantry
(gantry moves pipette into bar) and SO-101 (arm approaches at angle).

Designed for AELAB dPette 7016 and DLAB dPette+ ejector levers.

Usage:
    uv run --group cad python hardware/cad/tip_ejection_bar.py
"""

from pathlib import Path

import cadquery as cq

# --- Parameters (all in mm) ---
# Bar dimensions (the part that contacts the ejector lever)
BAR_LENGTH = 40.0  # Wide enough for 8-channel dPette+
BAR_WIDTH = 6.0
BAR_HEIGHT = 3.0

# Support bracket (L-shape, bolts to frame or bench)
BRACKET_HEIGHT = 50.0  # Tall enough to reach pipette ejector height
BRACKET_DEPTH = 25.0
WALL = 3.0

# Mounting
BOLT_HOLE_D = 4.2  # M4 clearance
BOLT_SPACING = 20.0


def build_tip_ejection_bar() -> cq.Workplane:
    """Build tip ejection bar with L-bracket mount."""
    # Vertical support plate
    support = cq.Workplane("XY").box(BAR_LENGTH, WALL, BRACKET_HEIGHT)

    # Horizontal bar at top (contacts ejector lever)
    bar = cq.Workplane("XY").box(BAR_LENGTH, BAR_WIDTH, BAR_HEIGHT)
    bar = bar.translate((0, BAR_WIDTH / 2 - WALL / 2, BRACKET_HEIGHT / 2 - BAR_HEIGHT / 2))

    # Base foot (for bolting to frame/bench)
    foot = cq.Workplane("XY").box(BAR_LENGTH, BRACKET_DEPTH, WALL)
    foot = foot.translate((0, BRACKET_DEPTH / 2 - WALL / 2, -BRACKET_HEIGHT / 2 + WALL / 2))

    part = support.union(bar).union(foot)

    # Mounting holes in base foot (2x M4)
    part = (
        part.faces("<Z")
        .workplane()
        .pushPoints([(-BOLT_SPACING / 2, 5), (BOLT_SPACING / 2, 5)])
        .hole(BOLT_HOLE_D)
    )

    return part


def export(part: cq.Workplane) -> None:
    """Export to STL and SVG."""
    stl = Path(__file__).parent.parent / "stl" / "tip_ejection_bar.stl"
    svg = Path(__file__).parent.parent / "svg" / "tip_ejection_bar.svg"
    cq.exporters.export(part, str(stl))
    cq.exporters.export(part, str(svg), exportType="SVG")
    print(f"Exported: {stl}")
    print(f"Exported: {svg}")


if __name__ == "__main__":
    export(build_tip_ejection_bar())
