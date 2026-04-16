"""Tests for coordinate_cmd.py — direct main() invocation for coverage."""

from __future__ import annotations

import logging

import pytest

from so101.coordinate_cmd import main


class TestCoordinateCmd:
    """Test coordinate command script via direct main() call."""

    def test_well_command(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--well A1 exits 0 and logs coordinates."""
        monkeypatch.setattr("sys.argv", ["so101-coord", "--well", "A1"])
        with caplog.at_level(logging.INFO):
            main()
        assert "A1" in caplog.text

    def test_park_command(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """--park exits 0."""
        monkeypatch.setattr("sys.argv", ["so101-coord", "--park"])
        with caplog.at_level(logging.INFO):
            main()
        assert "Parking" in caplog.text

    def test_missing_well_and_park(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """No --well and no --park exits non-zero."""
        monkeypatch.setattr("sys.argv", ["so101-coord"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0

    def test_invalid_well(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """--well Z99 exits non-zero (invalid well name)."""
        monkeypatch.setattr("sys.argv", ["so101-coord", "--well", "Z99"])
        with pytest.raises(ValueError, match="Invalid well name"):
            main()
