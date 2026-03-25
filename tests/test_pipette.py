"""Tests for DigitalPipette over-aspiration guard and basic operations."""

import pytest

from biolab.pipette import DigitalPipette, PipetteConfig


@pytest.fixture
def pipette() -> DigitalPipette:
    """Return a pipette in stub mode (no serial hardware)."""
    p = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB_MISSING", max_volume_ul=200.0))
    p.connect()
    return p


class TestPipetteAspirate:
    """Tests for aspirate guard logic."""

    def test_aspirate_within_capacity(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(100.0)
        assert pipette._current_fill == pytest.approx(100.0)

    def test_aspirate_exceeds_capacity(self, pipette: DigitalPipette) -> None:
        with pytest.raises(ValueError, match="exceeds max"):
            pipette.aspirate(250.0)

    def test_cumulative_aspirate_exceeds(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(150.0)
        with pytest.raises(ValueError, match="exceed"):
            pipette.aspirate(100.0)  # 150 + 100 = 250 > 200


class TestPipetteDispense:
    """Tests for dispense guard logic."""

    def test_dispense_within_fill(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(100.0)
        pipette.dispense(50.0)
        assert pipette._current_fill == pytest.approx(50.0)

    def test_dispense_exceeds_fill(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(50.0)
        with pytest.raises(ValueError, match="exceed"):
            pipette.dispense(100.0)


class TestPipetteConnect:
    """Tests for connection and stub mode."""

    def test_connect_stub_mode(self) -> None:
        """connect() must not crash when the serial port does not exist."""
        p = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB_MISSING"))
        p.connect()  # should not raise; falls through to stub mode


class TestVolumeToSteps:
    """Tests for _volume_to_steps boundary values."""

    def test_volume_to_steps_zero(self, pipette: DigitalPipette) -> None:
        assert pipette._volume_to_steps(0.0) == 0

    def test_volume_to_steps_max(self, pipette: DigitalPipette) -> None:
        steps = pipette._volume_to_steps(pipette.config.max_volume_ul)
        assert steps == 1023
