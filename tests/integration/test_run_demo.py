"""Tests for run_demo.py — calls main() directly for coverage instrumentation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from so101.run_demo import main

if TYPE_CHECKING:
    import pytest


class TestRunDemo:
    """Test demo orchestrator by invoking main() in-process."""

    def test_demo_full_mode(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--mode full exits 0 in stub mode."""
        monkeypatch.setattr("sys.argv", ["so101-demo", "--mode", "full"])
        with caplog.at_level(logging.INFO):
            main()
        assert "Demo complete" in caplog.text

    def test_demo_eval_mode(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--mode eval exits 0 in stub mode."""
        monkeypatch.setattr("sys.argv", ["so101-demo", "--mode", "eval"])
        with caplog.at_level(logging.INFO):
            main()
        assert "Demo complete" in caplog.text
