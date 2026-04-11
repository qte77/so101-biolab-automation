"""Tests for CAD SVG generation quality (CadQuery primary, OpenSCAD fallback).

Verifies that SVGs are isometric projections rather than flat top-down outlines.
Flat projection of a cylinder yields a circle (few segments); isometric
projection yields an ellipse with rich path data.

Part lists are driven by hardware/parts.json manifest.
"""

from __future__ import annotations

import json
import re

import pytest

from _paths import HARDWARE_DIR

SVG_DIR = HARDWARE_DIR / "svg"
MANIFEST = json.loads((HARDWARE_DIR / "parts.json").read_text())

# Derive part lists from manifest "shape" field — skip deferred/planned parts (no SVGs)
_RENDERABLE = [p for p in MANIFEST if p.get("status") not in ("planned", "deferred")]
COMPLEX_PARTS = [p["svg"].removesuffix(".svg") for p in _RENDERABLE if p["shape"] == "complex"]
BOX_PARTS = [p["svg"].removesuffix(".svg") for p in _RENDERABLE if p["shape"] == "box"]


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
    def test_box_part_has_wireframe_edges(self, part: str) -> None:
        """Box-shaped parts must show multiple edges (wireframe), not just an outline.

        CadQuery SVG export renders visible edges with hidden-line removal,
        producing lines/paths for each visible face edge. A box has >=7 visible
        edges in isometric view. A flat silhouette has only 4 points.
        """
        svg_path = SVG_DIR / f"{part}.svg"
        svg_text = svg_path.read_text()

        # Count distinct drawing elements (line, path, polyline)
        lines = len(re.findall(r"<line\b", svg_text))
        paths = len(re.findall(r"<path\b", svg_text))
        polylines = len(re.findall(r"<polyline\b", svg_text))
        total_edges = lines + paths + polylines

        # A wireframe box in isometric has many edges; a silhouette has 1 path
        assert total_edges > 1 or _count_path_points(svg_text) > 6, (
            f"{part}.svg has only {total_edges} drawing elements with "
            f"{_count_path_points(svg_text)} path points — "
            f"needs wireframe rendering (CadQuery SVG), not silhouette"
        )

    def test_all_stl_parts_have_svgs(self) -> None:
        """Every STL must have a corresponding SVG."""
        stl_dir = SVG_DIR.parent / "stl"
        stls = {p.stem for p in stl_dir.glob("*.stl")}
        svgs = {p.stem for p in SVG_DIR.glob("*.svg") if p.stem != "system_overview"}

        missing = stls - svgs
        assert not missing, f"STLs without SVGs: {missing}"


class TestManifest:
    """Validate hardware/parts.json against files on disk."""

    def test_manifest_scad_files_exist(self) -> None:
        for p in MANIFEST:
            if "scad" not in p:
                continue
            path = HARDWARE_DIR / p["scad"]
            assert path.exists(), f"Manifest references missing .scad: {p['scad']}"

    def test_manifest_cad_files_exist(self) -> None:
        for p in MANIFEST:
            if "cad" not in p:
                continue
            path = HARDWARE_DIR / p["cad"]
            assert path.exists(), f"Manifest references missing .py: {p['cad']}"

    def test_manifest_has_required_fields(self) -> None:
        always_required = {"name", "stl", "svg", "shape", "status"}
        impl_required = {"cad", "build_func"}  # required unless status=planned
        for part in MANIFEST:
            missing = always_required - set(part.keys())
            assert not missing, f"{part['name']} missing fields: {missing}"
            if part.get("status") != "planned":
                missing_impl = impl_required - set(part.keys())
                assert not missing_impl, f"{part['name']} missing fields: {missing_impl}"

    def test_manifest_shapes_are_valid(self) -> None:
        valid = {"complex", "box"}
        for part in MANIFEST:
            assert part["shape"] in valid, f"{part['name']} has invalid shape: {part['shape']}"

    def test_manifest_status_field_valid(self) -> None:
        valid = {"active", "redesign", "deferred", "planned"}
        for part in MANIFEST:
            assert "status" in part, f"{part['name']} missing status field"
            assert part["status"] in valid, f"{part['name']} has invalid status: {part['status']}"

    def test_manifest_primary_backend_valid(self) -> None:
        valid = {"build123d", "cadquery", "openscad"}
        for part in MANIFEST:
            assert "primary_backend" in part, f"{part['name']} missing primary_backend field"
            assert part["primary_backend"] in valid, (
                f"{part['name']} has invalid primary_backend: {part['primary_backend']}"
            )

    def test_manifest_notes_field_present(self) -> None:
        for part in MANIFEST:
            assert "notes" in part, f"{part['name']} missing notes field"
            assert len(part["notes"]) > 0, f"{part['name']} has empty notes"
