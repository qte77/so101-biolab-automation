"""Tests for hardware/slicer/validate.py — mocked subprocess, no slicer required."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Import module under test (not a package, lives outside src/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hardware" / "slicer"))
validate = importlib.import_module("validate")
sys.path.pop(0)

BACKEND = "prusa"
BINARY = "prusa-slicer"


@pytest.fixture
def tmp_stl(tmp_path: Path) -> Path:
    """Create a minimal dummy STL file."""
    stl = tmp_path / "test_part.stl"
    stl.write_text("solid test\nendsolid test\n")
    return stl


@pytest.fixture
def profile_path() -> Path:
    return validate.PROFILE_DIR / "pla_plus_02mm.ini"


class TestGetProfile:
    def test_default_is_pla(self) -> None:
        profile = validate.get_profile("plate_holder.stl", "prusa")
        assert "pla" in profile.name.lower()

    def test_tpu_for_gripper_tips(self) -> None:
        profile = validate.get_profile("gripper_tips_tpu.stl", "prusa")
        assert "tpu" in profile.name.lower()

    def test_override_tpu(self) -> None:
        profile = validate.get_profile("plate_holder.stl", "prusa", override="tpu")
        assert "tpu" in profile.name.lower()

    def test_cura_returns_json(self) -> None:
        profile = validate.get_profile("plate_holder.stl", "cura")
        assert profile.suffix == ".json"

    def test_prusa_returns_ini(self) -> None:
        profile = validate.get_profile("plate_holder.stl", "prusa")
        assert profile.suffix == ".ini"


class TestValidateStl:
    @patch("subprocess.run")
    def test_pass_on_clean_slice(self, mock_run, tmp_stl: Path, profile_path: Path) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Slicing done\n", stderr=""
        )
        result = validate.validate_stl(tmp_stl, BACKEND, BINARY, profile_path)
        assert result["status"] == "PASS"
        assert result["warnings"] == []

    @patch("subprocess.run")
    def test_warn_on_overhang(self, mock_run, tmp_stl: Path, profile_path: Path) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Warning: overhang detected at layer 5\n",
            stderr="",
        )
        result = validate.validate_stl(tmp_stl, BACKEND, BINARY, profile_path)
        assert result["status"] == "WARN"
        assert "overhang" in result["warnings"]

    @patch("subprocess.run")
    def test_fail_on_nonzero_exit(self, mock_run, tmp_stl: Path, profile_path: Path) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Error: invalid mesh"
        )
        result = validate.validate_stl(tmp_stl, BACKEND, BINARY, profile_path)
        assert result["status"] == "FAIL"
        assert result["error"] is not None

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="", timeout=120))
    def test_skip_on_timeout(self, mock_run, tmp_stl: Path, profile_path: Path) -> None:
        result = validate.validate_stl(tmp_stl, BACKEND, BINARY, profile_path)
        assert result["status"] == "SKIP"
        assert "Timeout" in result["error"]

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_skip_on_missing_binary(self, mock_run, tmp_stl: Path, profile_path: Path) -> None:
        result = validate.validate_stl(tmp_stl, BACKEND, BINARY, profile_path)
        assert result["status"] == "SKIP"

    @patch("subprocess.run")
    def test_detects_multiple_keywords(self, mock_run, tmp_stl: Path, profile_path: Path) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="overhang at layer 3, bridge detected\n",
            stderr="unsupported area found",
        )
        result = validate.validate_stl(tmp_stl, BACKEND, BINARY, profile_path)
        assert result["status"] == "WARN"
        assert "overhang" in result["warnings"]
        assert "bridge" in result["warnings"]
        assert "unsupported" in result["warnings"]


class TestMeshIntegrity:
    """Tests for STL binary mesh integrity check."""

    def test_structural_valid_stl(self, tmp_path: Path) -> None:
        """A valid binary STL with triangles passes."""
        import struct

        stl = tmp_path / "valid.stl"
        header = b"\x00" * 80
        num_triangles = 2
        triangle = struct.pack("<12fH", 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0)
        stl.write_bytes(header + struct.pack("<I", num_triangles) + triangle * num_triangles)
        result = validate.check_mesh_integrity(stl)
        assert result["status"] == "PASS"
        assert result["triangle_count"] == 2

    def test_structural_empty_file_fails(self, tmp_path: Path) -> None:
        """An empty file fails integrity check."""
        stl = tmp_path / "empty.stl"
        stl.write_bytes(b"")
        result = validate.check_mesh_integrity(stl)
        assert result["status"] == "FAIL"

    def test_structural_zero_triangles_fails(self, tmp_path: Path) -> None:
        """A file with 0 triangles fails."""
        import struct

        stl = tmp_path / "zero.stl"
        stl.write_bytes(b"\x00" * 80 + struct.pack("<I", 0))
        result = validate.check_mesh_integrity(stl)
        assert result["status"] == "FAIL"


class TestPrintReport:
    def test_all_pass(self, capsys) -> None:
        results = [
            {
                "file": "a.stl", "profile": "pla", "slicer": "prusa",
                "warnings": [], "status": "PASS", "error": None,
            }
        ]
        code = validate.print_report(results)
        assert code == 0
        assert "1/1" in capsys.readouterr().out

    def test_fail_returns_nonzero(self) -> None:
        results = [
            {
                "file": "a.stl", "profile": "pla", "slicer": "prusa",
                "warnings": [], "status": "FAIL", "error": "bad",
            }
        ]
        code = validate.print_report(results)
        assert code == 1

    def test_empty_results(self) -> None:
        code = validate.print_report([])
        assert code == 1
