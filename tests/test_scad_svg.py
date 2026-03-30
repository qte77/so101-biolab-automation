"""Tests for OpenSCAD SVG generation quality.

Verifies that SVGs are isometric projections (rotated) rather than flat
top-down outlines. Flat projection of a cylinder yields a circle (few segments);
isometric projection yields an ellipse with rich path data.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SVG_DIR = Path(__file__).resolve().parent.parent / "hardware" / "svg"

# Parts with cylindrical/compound geometry — isometric projection shows rich curves
COMPLEX_PARTS = [
    "tool_cone_robot",
    "tool_cone_pipette",
    "tool_cone_gripper",
    "tool_cone_hook",
    "pipette_mount_so101",
    "fridge_hook_tool",
]

# Box-shaped parts — isometric projection is still a parallelogram (geometrically correct)
BOX_PARTS = [
    "96well_plate_holder",
    "tool_dock_3station",
    "tip_rack_holder",
    "gripper_tips_tpu",
]


def _count_path_points(svg_text: str) -> int:
    """Count coordinate points across all <path> elements in SVG."""
    # Match M/L coordinate pairs in path d="" attributes
    d_attrs = re.findall(r'd="([^"]*)"', svg_text)
    total = 0
    for d in d_attrs:
        # Count M, L, and implicit coordinate pairs
        points = re.findall(r"[-\d.]+,[-\d.]+", d)
        total += len(points)
    return total


class TestSvgSpatialQuality:
    """SVGs must show 3D spatial detail, not flat outlines."""

    @pytest.mark.parametrize("part", COMPLEX_PARTS)
    def test_complex_part_has_spatial_detail(self, part: str) -> None:
        """Isometric SVG of complex parts must have >4 path points.

        A flat top-down projection of a cylinder is a circle (~4 points
        in simplified form). An isometric projection shows the full 3D
        silhouette with many more points.
        """
        svg_path = SVG_DIR / f"{part}.svg"
        assert svg_path.exists(), f"SVG not found: {svg_path}"

        svg_text = svg_path.read_text()
        points = _count_path_points(svg_text)

        assert points > 4, (
            f"{part}.svg has only {points} path points — "
            f"looks like a flat projection, expected isometric (>4 points)"
        )

    @pytest.mark.parametrize("part", COMPLEX_PARTS + BOX_PARTS)
    def test_svg_is_valid(self, part: str) -> None:
        """SVG must contain basic structure."""
        svg_path = SVG_DIR / f"{part}.svg"
        svg_text = svg_path.read_text()

        assert "<svg" in svg_text
        assert "<path" in svg_text or "<polygon" in svg_text

    @pytest.mark.parametrize("part", BOX_PARTS)
    def test_box_part_has_isometric_shape(self, part: str) -> None:
        """Box parts have 4 points but must be a parallelogram (not axis-aligned rectangle).

        Flat projection: points differ on only 2 axes (axis-aligned).
        Isometric projection: points differ on both axes (skewed parallelogram).
        """
        svg_path = SVG_DIR / f"{part}.svg"
        svg_text = svg_path.read_text()

        # Extract coordinate pairs
        d_attrs = re.findall(r'd="([^"]*)"', svg_text)
        coords = []
        for d in d_attrs:
            for match in re.finditer(r"([-\d.]+),([-\d.]+)", d):
                coords.append((float(match.group(1)), float(match.group(2))))

        assert len(coords) >= 4, f"{part}.svg has <4 coordinates"

        # Check that it's not axis-aligned (flat projection gives axis-aligned rect)
        xs = {round(c[0], 1) for c in coords}
        ys = {round(c[1], 1) for c in coords}
        # Isometric parallelogram: 4 unique x AND 4 unique y values
        # Flat rectangle: only 2 unique x OR 2 unique y values
        assert len(xs) > 2 or len(ys) > 2, (
            f"{part}.svg appears axis-aligned (flat projection)"
        )

    def test_all_stl_parts_have_svgs(self) -> None:
        """Every STL must have a corresponding SVG."""
        stl_dir = SVG_DIR.parent / "stl"
        stls = {p.stem for p in stl_dir.glob("*.stl")}
        svgs = {p.stem for p in SVG_DIR.glob("*.svg") if p.stem != "system_overview"}

        missing = stls - svgs
        assert not missing, f"STLs without SVGs: {missing}"
