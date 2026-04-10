"""Tests for dual arm controller — must work without LeRobot hardware."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from so101.arms import ArmConfig, DualArmConfig, DualArmController


@pytest.fixture
def stub_config() -> DualArmConfig:
    """Create a config for stub-mode testing."""
    return DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
        leader=ArmConfig(arm_id="leader", port="/dev/null", role="leader"),
        positions={"park": [0.0, -45.0, -90.0, 0.0, 0.0, 0.0]},
    )


@pytest.fixture
def connected_stub(stub_config: DualArmConfig) -> DualArmController:
    """Create a connected stub controller."""
    ctrl = DualArmController(stub_config)
    ctrl.connect()
    return ctrl


class TestDualArmController:
    """Test DualArmController in stub mode (no LeRobot)."""

    def test_connect_enables_operations(self, stub_config: DualArmConfig) -> None:
        """After connect(), arm operations work without raising."""
        ctrl = DualArmController(stub_config)
        ctrl.connect()
        obs = ctrl.get_observation("arm_a")
        assert "joints" in obs

    def test_disconnect_prevents_operations(self, connected_stub: DualArmController) -> None:
        """After disconnect(), arm operations raise ValueError."""
        connected_stub.disconnect()
        with pytest.raises(ValueError):
            connected_stub.get_observation("arm_a")

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


class TestNamedPositions:
    """Config-driven named positions loaded from YAML."""

    @pytest.fixture
    def positions_yaml(self, tmp_path: Path) -> Path:
        """Create a config with named positions."""
        cfg = {
            "arm_a": {"arm_id": "arm_a", "port": "/dev/null", "role": "follower"},
            "arm_b": {"arm_id": "arm_b", "port": "/dev/null", "role": "follower"},
            "positions": {
                "park": [0.0, -45.0, -90.0, 0.0, 0.0, 0.0],
                "home": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "well_approach": [10.0, -30.0, -60.0, 5.0, 0.0, 0.0],
            },
        }
        path = tmp_path / "arms.yaml"
        path.write_text(yaml.dump(cfg))
        return path

    @pytest.fixture
    def no_positions_yaml(self, tmp_path: Path) -> Path:
        """Create a config without positions section."""
        cfg = {
            "arm_a": {"arm_id": "arm_a", "port": "/dev/null", "role": "follower"},
            "arm_b": {"arm_id": "arm_b", "port": "/dev/null", "role": "follower"},
        }
        path = tmp_path / "arms.yaml"
        path.write_text(yaml.dump(cfg))
        return path

    def test_config_loads_positions(self, positions_yaml: Path) -> None:
        """DualArmConfig.from_yaml parses positions dict."""
        config = DualArmConfig.from_yaml(positions_yaml)
        assert config.positions == {
            "park": [0.0, -45.0, -90.0, 0.0, 0.0, 0.0],
            "home": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "well_approach": [10.0, -30.0, -60.0, 5.0, 0.0, 0.0],
        }

    def test_config_defaults_empty_positions(self, no_positions_yaml: Path) -> None:
        """DualArmConfig.from_yaml defaults to empty dict when no positions."""
        config = DualArmConfig.from_yaml(no_positions_yaml)
        assert config.positions == {}

    def test_move_to_named_sends_position(self, positions_yaml: Path) -> None:
        """move_to_named looks up position by name and sends to arm."""
        config = DualArmConfig.from_yaml(positions_yaml)
        ctrl = DualArmController(config)
        ctrl.connect()
        # Should not raise — sends the looked-up joint array
        ctrl.move_to_named("arm_a", "park")

    def test_move_to_named_unknown_position_raises(self, positions_yaml: Path) -> None:
        """move_to_named raises KeyError for unknown position name."""
        config = DualArmConfig.from_yaml(positions_yaml)
        ctrl = DualArmController(config)
        ctrl.connect()
        with pytest.raises(KeyError, match="no_such_position"):
            ctrl.move_to_named("arm_a", "no_such_position")

    def test_move_to_named_unknown_arm_raises(self, positions_yaml: Path) -> None:
        """move_to_named raises ValueError for unknown arm ID."""
        config = DualArmConfig.from_yaml(positions_yaml)
        ctrl = DualArmController(config)
        ctrl.connect()
        with pytest.raises(ValueError, match="Unknown arm"):
            ctrl.move_to_named("nonexistent", "park")


class TestConfigDrivenOperations:
    """park_all and send_to_well use config positions, not hardcoded values."""

    @pytest.fixture
    def config_with_positions(self) -> DualArmConfig:
        """Config with custom park and well_approach positions."""
        return DualArmConfig(
            arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
            arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
            positions={
                "park": [5.0, -40.0, -85.0, 2.0, 1.0, 0.0],
                "well_approach": [10.0, -30.0, -60.0, 5.0, 0.0, 0.0],
            },
        )

    def test_park_all_uses_config_position(
        self, config_with_positions: DualArmConfig
    ) -> None:
        """park_all sends the config 'park' position, not the hardcoded constant."""
        ctrl = DualArmController(config_with_positions)
        ctrl.connect()
        sent_actions: list[tuple[str, list[float]]] = []
        original_send = ctrl.send_action

        def spy_send(arm_id: str, action: list[float]) -> None:
            sent_actions.append((arm_id, action))
            original_send(arm_id, action)

        with patch.object(ctrl, "send_action", side_effect=spy_send):
            ctrl.park_all()

        # Both arms should receive the config park position
        assert len(sent_actions) == 2
        for arm_id, action in sent_actions:
            assert action == [5.0, -40.0, -85.0, 2.0, 1.0, 0.0]

    def test_send_to_well_uses_config_position(
        self, config_with_positions: DualArmConfig
    ) -> None:
        """send_to_well uses well_approach from config, not zero-filled stub."""
        ctrl = DualArmController(config_with_positions)
        ctrl.connect()
        sent_actions: list[tuple[str, list[float]]] = []
        original_send = ctrl.send_action

        def spy_send(arm_id: str, action: list[float]) -> None:
            sent_actions.append((arm_id, action))
            original_send(arm_id, action)

        with patch.object(ctrl, "send_action", side_effect=spy_send):
            ctrl.send_to_well("arm_a", "A1")

        assert len(sent_actions) == 1
        _, action = sent_actions[0]
        # Must NOT be all-zeros stub
        assert action != [0.0] * 6
        # Should be the well_approach position from config
        assert action == [10.0, -30.0, -60.0, 5.0, 0.0, 0.0]


class TestExecuteSequence:
    """execute_sequence sends named positions in order."""

    @pytest.fixture
    def seq_config(self) -> DualArmConfig:
        """Config with multiple positions for sequence testing."""
        return DualArmConfig(
            arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
            arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
            positions={
                "park": [0.0, -45.0, -90.0, 0.0, 0.0, 0.0],
                "home": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "approach": [10.0, -30.0, -60.0, 5.0, 0.0, 0.0],
                "lower": [10.0, -30.0, -80.0, 5.0, 0.0, 0.0],
            },
        )

    def test_sequence_sends_positions_in_order(self, seq_config: DualArmConfig) -> None:
        """execute_sequence sends each position to the arm in order."""
        ctrl = DualArmController(seq_config)
        ctrl.connect()
        sent: list[list[float]] = []
        original_send = ctrl.send_action

        def spy(arm_id: str, action: list[float]) -> None:
            sent.append(action)
            original_send(arm_id, action)

        with patch.object(ctrl, "send_action", side_effect=spy):
            ctrl.execute_sequence("arm_a", ["home", "approach", "lower"])

        assert len(sent) == 3
        assert sent[0] == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        assert sent[1] == [10.0, -30.0, -60.0, 5.0, 0.0, 0.0]
        assert sent[2] == [10.0, -30.0, -80.0, 5.0, 0.0, 0.0]

    def test_sequence_validates_all_names_before_sending(
        self, seq_config: DualArmConfig
    ) -> None:
        """execute_sequence raises KeyError if any name is invalid, sends nothing."""
        ctrl = DualArmController(seq_config)
        ctrl.connect()
        sent: list[list[float]] = []
        original_send = ctrl.send_action

        def spy(arm_id: str, action: list[float]) -> None:
            sent.append(action)
            original_send(arm_id, action)

        with patch.object(ctrl, "send_action", side_effect=spy), pytest.raises(
            KeyError, match="bogus"
        ):
            ctrl.execute_sequence("arm_a", ["home", "bogus", "approach"])

        # No actions should have been sent
        assert len(sent) == 0

    def test_sequence_empty_list_is_noop(self, seq_config: DualArmConfig) -> None:
        """execute_sequence with empty list does nothing."""
        ctrl = DualArmController(seq_config)
        ctrl.connect()
        ctrl.execute_sequence("arm_a", [])

    def test_sequence_unknown_arm_raises(self, seq_config: DualArmConfig) -> None:
        """execute_sequence raises ValueError for unknown arm."""
        ctrl = DualArmController(seq_config)
        ctrl.connect()
        with pytest.raises(ValueError, match="Unknown arm"):
            ctrl.execute_sequence("nonexistent", ["home"])
