"""Shared path constants for tests. Single source of truth for directory layout."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
HARDWARE_DIR = SRC_DIR / "hardware"  # code: cad/, scad/, slicer/, parts.json, render.py
ASSETS_DIR = PROJECT_ROOT / "hardware"  # generated assets: stl/, svg/, scans/
SO101_DIR = SRC_DIR / "so101"
CONFIGS_DIR = PROJECT_ROOT / "configs"
