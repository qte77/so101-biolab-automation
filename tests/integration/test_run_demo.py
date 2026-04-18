"""Tests for run_demo.py — calls main() directly for coverage instrumentation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from so101.cli.run_demo import main

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

    def test_uc1_single_well(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--use-case uc1_single dispatches to single-well pipetting."""
        monkeypatch.setattr(
            "sys.argv", ["so101-demo", "--use-case", "uc1_single", "--mode", "eval", "--well", "A1"]
        )
        with caplog.at_level(logging.INFO):
            main()
        assert "Demo complete" in caplog.text

    def test_uc2_fridge(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--use-case uc2 dispatches to fridge sequence."""
        monkeypatch.setattr("sys.argv", ["so101-demo", "--use-case", "uc2", "--mode", "eval"])
        with caplog.at_level(logging.INFO):
            main()
        assert "Demo complete" in caplog.text

    def test_uc3_tool_cycle(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--use-case uc3 dispatches to tool interchange cycle."""
        monkeypatch.setattr("sys.argv", ["so101-demo", "--use-case", "uc3", "--mode", "eval"])
        with caplog.at_level(logging.INFO):
            main()
        assert "Demo complete" in caplog.text
