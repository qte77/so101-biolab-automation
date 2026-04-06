"""Tests for pipette backends: DigitalPipette, ElectronicPipette, PipetteProtocol."""

import pytest

from biolab.pipette import (
    DigitalPipette,
    ElectronicPipette,
    ElectronicPipetteConfig,
    PipetteConfig,
    PipetteProtocol,
)


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


# ---------------------------------------------------------------------------
# ElectronicPipette tests
# ---------------------------------------------------------------------------


@pytest.fixture
def electronic_pipette() -> ElectronicPipette:
    """Return an electronic pipette in stub mode."""
    p = ElectronicPipette(
        ElectronicPipetteConfig(serial_port="/dev/ttyACM_MISSING", max_volume_ul=1000.0)
    )
    p.connect()
    return p


class TestElectronicPipetteConnect:
    """Tests for connection and stub mode."""

    def test_connect_stub_mode(self) -> None:
        p = ElectronicPipette(ElectronicPipetteConfig(serial_port="/dev/ttyACM_MISSING"))
        p.connect()  # should not raise

    def test_default_model(self) -> None:
        p = ElectronicPipette(ElectronicPipetteConfig())
        assert p.config.model == "aelab_dpette_7016"


class TestElectronicPipetteAspirate:
    """Tests for aspirate guard logic."""

    def test_aspirate_within_capacity(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(500.0)
        assert electronic_pipette._current_fill == pytest.approx(500.0)

    def test_aspirate_exceeds_capacity(self, electronic_pipette: ElectronicPipette) -> None:
        with pytest.raises(ValueError, match="exceeds max"):
            electronic_pipette.aspirate(1500.0)

    def test_cumulative_aspirate_exceeds(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(800.0)
        with pytest.raises(ValueError, match="exceed"):
            electronic_pipette.aspirate(300.0)


class TestElectronicPipetteDispense:
    """Tests for dispense guard logic."""

    def test_dispense_within_fill(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(500.0)
        electronic_pipette.dispense(200.0)
        assert electronic_pipette._current_fill == pytest.approx(300.0)

    def test_dispense_exceeds_fill(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(50.0)
        with pytest.raises(ValueError, match="exceed"):
            electronic_pipette.dispense(100.0)


# ---------------------------------------------------------------------------
# PipetteProtocol tests
# ---------------------------------------------------------------------------


class TestPipetteProtocol:
    """Verify both backends satisfy PipetteProtocol."""

    def test_digital_pipette_satisfies_protocol(self) -> None:
        p = DigitalPipette(PipetteConfig())
        assert isinstance(p, PipetteProtocol)

    def test_electronic_pipette_satisfies_protocol(self) -> None:
        p = ElectronicPipette(ElectronicPipetteConfig())
        assert isinstance(p, PipetteProtocol)
