"""Tests for coordinate_cmd.py script."""

from __future__ import annotations

import subprocess
import sys


class TestCoordinateCmd:
    """Test coordinate command script via subprocess."""

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/coordinate_cmd.py", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_well_command(self) -> None:
        """--well A1 exits 0 and logs coordinates."""
        result = self._run("--well", "A1")
        assert result.returncode == 0
        assert "A1" in result.stderr  # logging goes to stderr

    def test_park_command(self) -> None:
        """--park exits 0."""
        result = self._run("--park")
        assert result.returncode == 0
        assert "Parking" in result.stderr

    def test_missing_well_and_park(self) -> None:
        """No --well and no --park exits non-zero."""
        result = self._run()
        assert result.returncode != 0

    def test_invalid_well(self) -> None:
        """--well Z99 exits non-zero (invalid well name)."""
        result = self._run("--well", "Z99")
        assert result.returncode != 0
