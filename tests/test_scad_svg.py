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

# Parts with enough 3D complexity to distinguish flat vs isometric
COMPLEX_PARTS = [
    "tool_cone_robot",
    "tool_cone_pipette",
    "tool_dock_3station",
    "pipette_mount_so101",
    "96well_plate_holder",
    "fridge_hook_tool",
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


def _count_paths(svg_text: str) -> int:
    """Count <path> elements in SVG."""
    return len(re.findall(r"<path\b", svg_text))


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

    @pytest.mark.parametrize("part", COMPLEX_PARTS)
    def test_svg_is_valid(self, part: str) -> None:
        """SVG must contain basic structure."""
        svg_path = SVG_DIR / f"{part}.svg"
        svg_text = svg_path.read_text()

        assert "<svg" in svg_text
        assert "<path" in svg_text or "<polygon" in svg_text

    def test_all_stl_parts_have_svgs(self) -> None:
        """Every STL must have a corresponding SVG."""
        stl_dir = SVG_DIR.parent / "stl"
        stls = {p.stem for p in stl_dir.glob("*.stl")}
        svgs = {p.stem for p in SVG_DIR.glob("*.svg") if p.stem != "system_overview"}

        missing = stls - svgs
        assert not missing, f"STLs without SVGs: {missing}"
