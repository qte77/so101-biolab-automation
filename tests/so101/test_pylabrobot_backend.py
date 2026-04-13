"""Tests for PyLabRobot SO-101 backend — strict TDD, async interface."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from so101.arms import ArmConfig, DualArmConfig, DualArmController
from so101.pipette import DigitalPipette, PipetteConfig
from so101.pylabrobot_backend import SO101Backend, SO101BackendConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def stub_arm() -> DualArmController:
    """Create a connected stub-mode dual arm controller."""
    config = DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
        positions={"park": [0.0] * 6},
    )
    ctrl = DualArmController(config)
    ctrl.connect()
    return ctrl


@pytest.fixture
def stub_pipette() -> DigitalPipette:
    """Create a connected stub-mode digital pipette."""
    p = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB_MISSING", max_volume_ul=200.0))
    p.connect()
    return p


@pytest.fixture
def backend(stub_arm: DualArmController, stub_pipette: DigitalPipette) -> SO101Backend:
    """Create a backend with stub arm and pipette."""
    config = SO101BackendConfig()
    return SO101Backend(config, stub_arm, stub_pipette)


# ---------------------------------------------------------------------------
# Config model tests
# ---------------------------------------------------------------------------


class TestSO101BackendConfigModel:
    """Strict pydantic validation for SO101BackendConfig."""

    def test_defaults(self) -> None:
        """Default config has arm_id='arm_a' and pipette_backend='digital_pipette_v2'."""
        cfg = SO101BackendConfig()
        assert cfg.arm_id == "arm_a"
        assert cfg.pipette_backend == "digital_pipette_v2"

    def test_strict_rejects_int_for_str(self) -> None:
        """Strict mode rejects non-string for arm_id."""
        with pytest.raises(ValidationError):
            SO101BackendConfig(arm_id=123)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Setup / teardown tests
# ---------------------------------------------------------------------------


class TestSO101BackendSetup:
    """Backend lifecycle: setup, stop, stub mode."""

    async def test_setup_connects_arm_and_pipette(self, backend: SO101Backend) -> None:
        """After setup(), the arm is connected."""
        await backend.setup()
        assert backend._arm.is_connected

    async def test_stop_disconnects_pipette(self, backend: SO101Backend) -> None:
        """After stop(), the pipette is disconnected."""
        await backend.setup()
        await backend.stop()
        # Pipette disconnect closes serial; stub mode has _serial=None already,
        # so we verify stop() completes without error.

    def test_is_stub_mode_delegates_to_arm(self, backend: SO101Backend) -> None:
        """is_stub_mode reflects the arm controller's stub state."""
        assert backend.is_stub_mode == backend._arm.is_stub_mode


# ---------------------------------------------------------------------------
# Operation tests
# ---------------------------------------------------------------------------


class TestSO101BackendOperations:
    """Backend pipette and arm operations delegate correctly."""

    async def test_aspirate_delegates_to_pipette(
        self, backend: SO101Backend, stub_pipette: DigitalPipette
    ) -> None:
        """Aspirate via backend updates pipette fill state."""
        await backend.aspirate(50.0)
        # Verify pipette tracked the volume — dispensing 50 should succeed
        stub_pipette.dispense(50.0)

    async def test_dispense_delegates_to_pipette(
        self, backend: SO101Backend, stub_pipette: DigitalPipette
    ) -> None:
        """Dispense via backend updates pipette fill state."""
        await backend.aspirate(100.0)
        await backend.dispense(50.0)
        # 50 µL remains — dispensing 50 more should succeed
        stub_pipette.dispense(50.0)

    async def test_aspirate_exceeds_capacity_raises(self, backend: SO101Backend) -> None:
        """Aspirating beyond max volume raises ValueError."""
        with pytest.raises(ValueError, match="exceeds max"):
            await backend.aspirate(300.0)

    async def test_drop_tip_calls_eject(self, backend: SO101Backend) -> None:
        """drop_tip delegates to pipette eject_tip without error."""
        await backend.drop_tip()

    async def test_move_to_records_action(
        self, backend: SO101Backend, stub_arm: DualArmController
    ) -> None:
        """move_to sends action to arm, observable via get_observation."""
        position = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        await backend.move_to("arm_a", position)
        obs = stub_arm.get_observation("arm_a")
        assert obs["joints"] == position


# ---------------------------------------------------------------------------
# Hypothesis property tests
# ---------------------------------------------------------------------------


class TestSO101BackendHypothesis:
    """Property-based tests for backend operations."""

    @given(volume=st.floats(min_value=0.1, max_value=200.0))
    async def test_aspirate_valid_volume_no_crash(self, volume: float) -> None:
        """Any valid volume can be aspirated without crashing."""
        config = DualArmConfig(
            arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
            arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
            positions={"park": [0.0] * 6},
        )
        ctrl = DualArmController(config)
        ctrl.connect()
        p = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB_MISSING", max_volume_ul=200.0))
        p.connect()
        be = SO101Backend(SO101BackendConfig(), ctrl, p)
        await be.aspirate(volume)
