"""Tests for BentoLab thermocycler controller."""

import pytest

from so101.bento_lab import BentoLab, BentoLabConfig


@pytest.fixture
def bento() -> BentoLab:
    """Return a Bento Lab in stub mode."""
    b = BentoLab(BentoLabConfig(serial_port="/dev/ttyACM_MISSING"))
    b.connect()
    return b


class TestBentoLabConnect:
    """Tests for connection and stub mode."""

    def test_connect_stub_mode(self) -> None:
        b = BentoLab(BentoLabConfig(serial_port="/dev/ttyACM_MISSING"))
        b.connect()  # should not raise

    def test_disconnect(self, bento: BentoLab) -> None:
        bento.disconnect()


class TestBentoLabLid:
    """Tests for lid open/close."""

    def test_open_close_lid(self, bento: BentoLab) -> None:
        """Lid state observable through get_status()."""
        bento.open_lid()
        assert bento.get_status()["lid_open"] is True
        bento.close_lid()
        assert bento.get_status()["lid_open"] is False


class TestBentoLabProgram:
    """Tests for PCR program control."""

    def test_start_program(self, bento: BentoLab) -> None:
        """Running program observable through get_status()."""
        bento.close_lid()
        bento.start_program("pcr_standard")
        status = bento.get_status()
        assert status["running"] is True
        assert status["program"] == "pcr_standard"

    def test_start_program_with_lid_open_raises(self, bento: BentoLab) -> None:
        bento.open_lid()
        with pytest.raises(ValueError, match="lid must be closed"):
            bento.start_program("pcr_standard")

    def test_get_status(self, bento: BentoLab) -> None:
        status = bento.get_status()
        assert "lid_open" in status
        assert "running" in status
        assert "program" in status
