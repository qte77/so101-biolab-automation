"""Autonomous tool changing for SO-101 arms.

Manages a 3-station magnetic dock where arms can swap end-effectors:
- Pipette (digital-pipette-v2)
- Gripper jaws (default SO-101 gripper)
- Fridge hook (custom 3D-printed)

Reference: Berkeley passive modular tool changer (3D-printed, magnetic).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class Tool(Enum):
    """Available end-effector tools."""

    NONE = "none"
    PIPETTE = "pipette"
    GRIPPER = "gripper"
    FRIDGE_HOOK = "fridge_hook"


class DockStation(BaseModel):
    """A single station on the tool dock."""

    model_config = ConfigDict(strict=True)

    tool: Tool
    approach_joints: list[float]  # Joint positions to approach the station
    engage_joints: list[float]  # Joint positions to engage/disengage
    dock_joints: list[float]  # Joint positions when docked


@dataclass
class ToolDockConfig:
    """Configuration for the 3-station tool dock."""

    stations: dict[str, DockStation]

    @classmethod
    def from_yaml(cls, path: str) -> ToolDockConfig:
        """Load dock configuration from YAML.

        Args:
            path: Path to tool_dock.yaml.

        Returns:
            ToolDockConfig instance.
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        stations = {}
        for name, station_data in data["stations"].items():
            stations[name] = DockStation(
                tool=Tool(station_data["tool"]),
                approach_joints=station_data["approach_joints"],
                engage_joints=station_data["engage_joints"],
                dock_joints=station_data["dock_joints"],
            )
        return cls(stations=stations)


class ToolChanger:
    """Manages tool changes for an SO-101 arm.

    Usage:
        changer = ToolChanger(dock_config, arm_controller, "arm_a")
        changer.change_tool(Tool.PIPETTE)
        # ... do pipetting work ...
        changer.change_tool(Tool.GRIPPER)
    """

    def __init__(self, config: ToolDockConfig, arm_controller: Any, arm_id: str) -> None:
        self.config = config
        self.arm = arm_controller
        self.arm_id = arm_id
        self.current_tool = Tool.GRIPPER  # Default: gripper installed

    def change_tool(self, target: Tool) -> None:
        """Change the current end-effector tool.

        Args:
            target: The tool to switch to.
        """
        if target == self.current_tool:
            logger.info("Already equipped with %s", target.value)
            return

        if self.current_tool != Tool.NONE:
            self._return_tool(self.current_tool)

        if target != Tool.NONE:
            self._pickup_tool(target)

        self.current_tool = target
        logger.info("Tool changed to %s", target.value)

    def _return_tool(self, tool: Tool) -> None:
        """Return current tool to its dock station.

        Args:
            tool: Tool to return.
        """
        station = self._find_station(tool)
        logger.info("Returning %s to dock", tool.value)

        # Approach → engage → open gripper → retract
        self.arm.send_action(self.arm_id, station.approach_joints)
        self.arm.send_action(self.arm_id, station.engage_joints)
        self.arm.send_action(self.arm_id, station.dock_joints)
        # Open gripper to release tool
        self.arm.send_action(self.arm_id, station.approach_joints)

    def _pickup_tool(self, tool: Tool) -> None:
        """Pick up a tool from its dock station.

        Args:
            tool: Tool to pick up.
        """
        station = self._find_station(tool)
        logger.info("Picking up %s from dock", tool.value)

        # Approach → engage → close gripper → retract
        self.arm.send_action(self.arm_id, station.approach_joints)
        self.arm.send_action(self.arm_id, station.dock_joints)
        self.arm.send_action(self.arm_id, station.engage_joints)
        # Close gripper to secure tool
        self.arm.send_action(self.arm_id, station.approach_joints)

    def _find_station(self, tool: Tool) -> DockStation:
        """Find the dock station for a given tool.

        Args:
            tool: Tool to find.

        Returns:
            DockStation for the tool.

        Raises:
            ValueError: If no station found for tool.
        """
        for station in self.config.stations.values():
            if station.tool == tool:
                return station
        raise ValueError(f"No dock station for tool: {tool.value}")
