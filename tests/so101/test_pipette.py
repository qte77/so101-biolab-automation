"""Tests for pipette backends — behavioral contracts only.

Tests verify observable outcomes (aspirate/dispense succeed or raise),
never internal state like _current_fill or _volume_to_steps.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from so101.pipette import (
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


@pytest.fixture
def electronic_pipette() -> ElectronicPipette:
    """Return an electronic pipette in stub mode."""
    p = ElectronicPipette(
        ElectronicPipetteConfig(serial_port="/dev/ttyACM_MISSING", max_volume_ul=1000.0)
    )
    p.connect()
    return p


class TestDigitalPipetteCapacity:
    """Aspirate/dispense capacity tracking through observable behavior."""

    def test_aspirate_within_capacity(self, pipette: DigitalPipette) -> None:
        """Aspirating within max volume does not raise."""
        pipette.aspirate(100.0)

    def test_aspirate_exceeds_capacity(self, pipette: DigitalPipette) -> None:
        with pytest.raises(ValueError, match="exceeds max"):
            pipette.aspirate(250.0)

    def test_cumulative_aspirate_exceeds(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(150.0)
        with pytest.raises(ValueError, match="exceed"):
            pipette.aspirate(100.0)

    def test_dispense_after_aspirate(self, pipette: DigitalPipette) -> None:
        """Dispensing exactly what was aspirated succeeds."""
        pipette.aspirate(100.0)
        pipette.dispense(100.0)

    def test_dispense_partial_then_remaining(self, pipette: DigitalPipette) -> None:
        """Partial dispense, then dispensing the rest succeeds."""
        pipette.aspirate(100.0)
        pipette.dispense(50.0)
        pipette.dispense(50.0)

    def test_dispense_exceeds_fill(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(50.0)
        with pytest.raises(ValueError, match="exceed"):
            pipette.dispense(100.0)

    def test_dispense_partial_then_exceeds(self, pipette: DigitalPipette) -> None:
        """After partial dispense, over-dispensing raises."""
        pipette.aspirate(100.0)
        pipette.dispense(50.0)
        with pytest.raises(ValueError, match="exceed"):
            pipette.dispense(51.0)


class TestDigitalPipetteConnect:
    def test_connect_stub_mode(self) -> None:
        """connect() does not crash when serial port missing."""
        p = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB_MISSING"))
        p.connect()


class TestElectronicPipetteCapacity:
    """Same behavioral contracts for electronic pipette."""

    def test_aspirate_within_capacity(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(500.0)

    def test_aspirate_exceeds_capacity(self, electronic_pipette: ElectronicPipette) -> None:
        with pytest.raises(ValueError, match="exceeds max"):
            electronic_pipette.aspirate(1500.0)

    def test_cumulative_aspirate_exceeds(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(800.0)
        with pytest.raises(ValueError, match="exceed"):
            electronic_pipette.aspirate(300.0)

    def test_dispense_after_aspirate(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(500.0)
        electronic_pipette.dispense(500.0)

    def test_dispense_partial_then_exceeds(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(500.0)
        electronic_pipette.dispense(200.0)
        with pytest.raises(ValueError, match="exceed"):
            electronic_pipette.dispense(301.0)

    def test_dispense_exceeds_fill(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.aspirate(50.0)
        with pytest.raises(ValueError, match="exceed"):
            electronic_pipette.dispense(100.0)


class TestElectronicPipetteConnect:
    def test_connect_stub_mode(self) -> None:
        p = ElectronicPipette(ElectronicPipetteConfig(serial_port="/dev/ttyACM_MISSING"))
        p.connect()


class TestDigitalPipetteEdgeCases:
    """Edge cases: zero/negative volumes, multi-cycle, eject_tip."""

    def test_zero_volume_aspirate_raises(self, pipette: DigitalPipette) -> None:
        with pytest.raises(ValueError, match="positive"):
            pipette.aspirate(0.0)

    def test_negative_volume_aspirate_raises(self, pipette: DigitalPipette) -> None:
        with pytest.raises(ValueError, match="positive"):
            pipette.aspirate(-10.0)

    def test_zero_volume_dispense_raises(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(50.0)
        with pytest.raises(ValueError, match="positive"):
            pipette.dispense(0.0)

    def test_negative_volume_dispense_raises(self, pipette: DigitalPipette) -> None:
        pipette.aspirate(50.0)
        with pytest.raises(ValueError, match="positive"):
            pipette.dispense(-5.0)

    def test_multi_cycle_roundtrip(self, pipette: DigitalPipette) -> None:
        """Aspirate full → dispense full repeated 3 times works."""
        for _ in range(3):
            pipette.aspirate(200.0)
            pipette.dispense(200.0)

    def test_eject_tip_stub(self, pipette: DigitalPipette) -> None:
        """eject_tip runs without error in stub mode."""
        pipette.eject_tip()


class TestElectronicPipetteEdgeCases:
    """Edge cases for electronic pipette."""

    def test_zero_volume_aspirate_raises(self, electronic_pipette: ElectronicPipette) -> None:
        with pytest.raises(ValueError, match="positive"):
            electronic_pipette.aspirate(0.0)

    def test_negative_volume_aspirate_raises(self, electronic_pipette: ElectronicPipette) -> None:
        with pytest.raises(ValueError, match="positive"):
            electronic_pipette.aspirate(-10.0)

    def test_multi_cycle_roundtrip(self, electronic_pipette: ElectronicPipette) -> None:
        for _ in range(3):
            electronic_pipette.aspirate(1000.0)
            electronic_pipette.dispense(1000.0)

    def test_eject_tip_stub(self, electronic_pipette: ElectronicPipette) -> None:
        electronic_pipette.eject_tip()


class TestPipetteProtocol:
    """Both backends satisfy the protocol interface."""

    def test_digital_pipette_satisfies_protocol(self) -> None:
        p = DigitalPipette(PipetteConfig())
        assert isinstance(p, PipetteProtocol)

    def test_electronic_pipette_satisfies_protocol(self) -> None:
        p = ElectronicPipette(ElectronicPipetteConfig())
        assert isinstance(p, PipetteProtocol)


class TestPipetteProperties:
    """Hypothesis property tests for aspirate/dispense roundtrip."""

    @given(volume=st.floats(min_value=0.1, max_value=200.0))
    def test_aspirate_dispense_roundtrip(self, volume: float) -> None:
        """Any valid volume can be aspirated then fully dispensed."""
        p = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB_MISSING", max_volume_ul=200.0))
        p.connect()
        p.aspirate(volume)
        p.dispense(volume)
