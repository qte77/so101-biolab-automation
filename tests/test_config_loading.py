"""Integration tests for config file loading."""

import pytest
import yaml

from biolab.arms import DualArmConfig
from biolab.tool_changer import ToolDockConfig


@pytest.mark.integration
class TestConfigLoading:
    """Verify real YAML config files parse correctly."""

    def test_arms_yaml_loads(self) -> None:
        """configs/arms.yaml loads into DualArmConfig."""
        config = DualArmConfig.from_yaml("configs/arms.yaml")
        assert config.arm_a.arm_id == "arm_a"
        assert config.arm_b.arm_id == "arm_b"
        assert config.arm_a.role == "follower"
        assert config.leader is not None
        assert config.leader.role == "leader"

    def test_tool_dock_yaml_loads(self) -> None:
        """configs/tool_dock.yaml loads into ToolDockConfig."""
        config = ToolDockConfig.from_yaml("configs/tool_dock.yaml")
        assert "pipette" in config.stations
        assert "gripper" in config.stations
        assert "fridge_hook" in config.stations

    def test_plate_layout_yaml_loads(self) -> None:
        """configs/plate_layout.yaml is valid YAML with expected keys."""
        with open("configs/plate_layout.yaml") as f:
            data = yaml.safe_load(f)
        assert "plate" in data
        assert "tip_rack" in data
        assert "heights" in data
        assert data["plate"]["well_spacing_mm"] == 9.0

    def test_arms_yaml_cameras_structure(self) -> None:
        """Camera config in arms.yaml has expected fields."""
        config = DualArmConfig.from_yaml("configs/arms.yaml")
        assert "wrist" in config.arm_a.cameras
        cam = config.arm_a.cameras["wrist"]
        assert cam["type"] == "opencv"
