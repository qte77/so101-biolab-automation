"""Tests for dual arm controller — must work without LeRobot hardware."""

import pytest

from biolab.arms import ArmConfig, DualArmConfig, DualArmController


@pytest.fixture
def stub_config() -> DualArmConfig:
    """Create a config for stub-mode testing."""
    return DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
        leader=ArmConfig(arm_id="leader", port="/dev/null", role="leader"),
    )


@pytest.fixture
def connected_stub(stub_config: DualArmConfig) -> DualArmController:
    """Create a connected stub controller."""
    ctrl = DualArmController(stub_config)
    ctrl.connect()
    return ctrl


class TestDualArmController:
    """Test DualArmController in stub mode (no LeRobot)."""

    def test_connect_stub_mode(self, stub_config: DualArmConfig) -> None:
        """connect() succeeds in stub mode without LeRobot."""
        ctrl = DualArmController(stub_config)
        ctrl.connect()
        assert ctrl._connected is True

    def test_disconnect_stub_mode(self, connected_stub: DualArmController) -> None:
        """disconnect() works in stub mode."""
        connected_stub.disconnect()
        assert connected_stub._connected is False

    def test_get_observation_stub(self, connected_stub: DualArmController) -> None:
        """get_observation returns stub data when no real robots connected."""
        obs = connected_stub.get_observation("arm_a")
        assert obs["stub"] is True
        assert "joints" in obs

    def test_send_action_stub(self, connected_stub: DualArmController) -> None:
        """send_action is a no-op in stub mode (no crash)."""
        connected_stub.send_action("arm_a", [0.0] * 6)

    def test_send_to_well(self, connected_stub: DualArmController) -> None:
        """send_to_well parses well name and calls send_action."""
        connected_stub.send_to_well("arm_a", "A1")

    def test_send_to_well_invalid(self, connected_stub: DualArmController) -> None:
        """send_to_well raises ValueError for invalid well name."""
        with pytest.raises(ValueError):
            connected_stub.send_to_well("arm_a", "Z99")

    def test_park_all(self, connected_stub: DualArmController) -> None:
        """park_all sends park position to both arms."""
        connected_stub.park_all()

    def test_get_observation_unknown_arm(self, connected_stub: DualArmController) -> None:
        """get_observation raises ValueError for unknown arm ID."""
        with pytest.raises(ValueError, match="Unknown arm"):
            connected_stub.get_observation("nonexistent")
