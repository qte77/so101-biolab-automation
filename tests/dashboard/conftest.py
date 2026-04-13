"""Shared fixtures for dashboard tests — force stub mode via environment variable."""

import pytest


@pytest.fixture(autouse=True)
def _force_stub_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set SO101_STUB_MODE=1 so DualArmController always enters stub mode."""
    monkeypatch.setenv("SO101_STUB_MODE", "1")
