"""Tests for run_demo.py script."""

from __future__ import annotations

import subprocess
import sys


class TestRunDemo:
    """Test demo orchestrator script via subprocess."""

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/run_demo.py", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_demo_full_mode(self) -> None:
        """--mode full exits 0 in stub mode."""
        result = self._run("--mode", "full")
        assert result.returncode == 0
        assert "Demo complete" in result.stderr

    def test_demo_eval_mode(self) -> None:
        """--mode eval exits 0 in stub mode."""
        result = self._run("--mode", "eval")
        assert result.returncode == 0
        assert "Demo complete" in result.stderr
