"""Shared fixtures for so101 tests — force stub mode via environment variable."""

import pytest


@pytest.fixture(autouse=True)
def _force_stub_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set SO101_STUB_MODE=1 so DualArmController always enters stub mode.

    Works for both in-process tests and subprocess-based integration tests.
    """
    monkeypatch.setenv("SO101_STUB_MODE", "1")
