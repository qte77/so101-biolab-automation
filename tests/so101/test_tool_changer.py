"""Tests for tool changer logic."""

import pytest

from so101.tool_changer import DockStation, Tool, ToolChanger, ToolDockConfig


@pytest.fixture
def dock_config() -> ToolDockConfig:
    """Create a test dock configuration."""
    return ToolDockConfig(
        stations={
            "pipette": DockStation(
                tool=Tool.PIPETTE,
                approach_joints=[0.0] * 6,
                engage_joints=[1.0] * 6,
                dock_joints=[2.0] * 6,
            ),
            "gripper": DockStation(
                tool=Tool.GRIPPER,
                approach_joints=[10.0] * 6,
                engage_joints=[11.0] * 6,
                dock_joints=[12.0] * 6,
            ),
        }
    )


class StubArmController:
    """Records actions sent to the arm."""

    def __init__(self) -> None:
        self.actions: list[tuple[str, list[float]]] = []

    def send_action(self, arm_id: str, action: list[float]) -> None:
        self.actions.append((arm_id, action))


class TestToolChanger:
    """Test tool change sequences."""

    def test_change_to_same_tool_is_noop(self, dock_config: ToolDockConfig) -> None:
        stub = StubArmController()
        changer = ToolChanger(dock_config, stub, "arm_a")
        changer.current_tool = Tool.GRIPPER
        changer.change_tool(Tool.GRIPPER)
        assert len(stub.actions) == 0

    def test_change_tool_returns_current_and_picks_new(self, dock_config: ToolDockConfig) -> None:
        stub = StubArmController()
        changer = ToolChanger(dock_config, stub, "arm_a")
        changer.current_tool = Tool.GRIPPER
        changer.change_tool(Tool.PIPETTE)
        assert changer.current_tool == Tool.PIPETTE
        # Return gripper (4 moves) + pickup pipette (4 moves) = 8 actions
        assert len(stub.actions) == 8

    def test_change_to_none_only_returns(self, dock_config: ToolDockConfig) -> None:
        stub = StubArmController()
        changer = ToolChanger(dock_config, stub, "arm_a")
        changer.current_tool = Tool.GRIPPER
        changer.change_tool(Tool.NONE)
        assert changer.current_tool == Tool.NONE
        assert len(stub.actions) == 4  # Return only

    def test_missing_station_raises(self, dock_config: ToolDockConfig) -> None:
        stub = StubArmController()
        changer = ToolChanger(dock_config, stub, "arm_a")
        changer.current_tool = Tool.NONE
        with pytest.raises(ValueError, match="fridge_hook"):
            changer.change_tool(Tool.FRIDGE_HOOK)

    def test_change_from_none_only_picks_up(self, dock_config: ToolDockConfig) -> None:
        """Starting with NONE, change_tool only does pickup (no return)."""
        stub = StubArmController()
        changer = ToolChanger(dock_config, stub, "arm_a")
        changer.current_tool = Tool.NONE
        changer.change_tool(Tool.PIPETTE)
        assert changer.current_tool == Tool.PIPETTE
        assert len(stub.actions) == 4  # Pickup only

    def test_rapid_tool_changes(self, dock_config: ToolDockConfig) -> None:
        """Two consecutive tool changes work correctly."""
        stub = StubArmController()
        changer = ToolChanger(dock_config, stub, "arm_a")
        changer.current_tool = Tool.NONE
        changer.change_tool(Tool.PIPETTE)
        changer.change_tool(Tool.GRIPPER)
        assert changer.current_tool == Tool.GRIPPER
        # 4 (pickup pipette) + 4 (return pipette) + 4 (pickup gripper) = 12
        assert len(stub.actions) == 12
