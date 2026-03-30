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
        profile = validate.get_profile("plate_holder.stl")
        assert "pla" in profile.name.lower()

    def test_tpu_for_gripper_tips(self) -> None:
        profile = validate.get_profile("gripper_tips_tpu.stl")
        assert "tpu" in profile.name.lower()

    def test_override_tpu(self) -> None:
        profile = validate.get_profile("plate_holder.stl", override="tpu")
        assert "tpu" in profile.name.lower()


class TestValidateStl:
    @patch("subprocess.run")
    def test_pass_on_clean_slice(
        self, mock_run, tmp_stl: Path, profile_path: Path
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Slicing done\n", stderr=""
        )
        result = validate.validate_stl(tmp_stl, profile_path)
        assert result["status"] == "PASS"
        assert result["warnings"] == []

    @patch("subprocess.run")
    def test_warn_on_overhang(
        self, mock_run, tmp_stl: Path, profile_path: Path
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Warning: overhang detected at layer 5\n",
            stderr="",
        )
        result = validate.validate_stl(tmp_stl, profile_path)
        assert result["status"] == "WARN"
        assert "overhang" in result["warnings"]

    @patch("subprocess.run")
    def test_fail_on_nonzero_exit(
        self, mock_run, tmp_stl: Path, profile_path: Path
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Error: invalid mesh"
        )
        result = validate.validate_stl(tmp_stl, profile_path)
        assert result["status"] == "FAIL"
        assert result["error"] is not None

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="", timeout=120))
    def test_skip_on_timeout(
        self, mock_run, tmp_stl: Path, profile_path: Path
    ) -> None:
        result = validate.validate_stl(tmp_stl, profile_path)
        assert result["status"] == "SKIP"
        assert "Timeout" in result["error"]

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_skip_on_missing_binary(
        self, mock_run, tmp_stl: Path, profile_path: Path
    ) -> None:
        result = validate.validate_stl(tmp_stl, profile_path)
        assert result["status"] == "SKIP"

    @patch("subprocess.run")
    def test_detects_multiple_keywords(
        self, mock_run, tmp_stl: Path, profile_path: Path
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="overhang at layer 3, bridge detected\n",
            stderr="unsupported area found",
        )
        result = validate.validate_stl(tmp_stl, profile_path)
        assert result["status"] == "WARN"
        assert "overhang" in result["warnings"]
        assert "bridge" in result["warnings"]
        assert "unsupported" in result["warnings"]


class TestPrintReport:
    def test_all_pass(self, capsys) -> None:
        results = [
            {"file": "a.stl", "profile": "pla", "warnings": [], "status": "PASS", "error": None}
        ]
        code = validate.print_report(results)
        assert code == 0
        assert "1/1" in capsys.readouterr().out

    def test_fail_returns_nonzero(self) -> None:
        results = [
            {"file": "a.stl", "profile": "pla", "warnings": [], "status": "FAIL", "error": "bad"}
        ]
        code = validate.print_report(results)
        assert code == 1

    def test_empty_results(self) -> None:
        code = validate.print_report([])
        assert code == 1
