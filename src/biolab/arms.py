"""Dual SO-101 arm controller wrapping LeRobot API.

Manages two follower arms and optional leader arm for teleoperation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from biolab.plate import parse_well_name
from biolab.safety import PARK_POSITION

logger = logging.getLogger(__name__)


@dataclass
class ArmConfig:
    """Configuration for a single SO-101 arm."""

    arm_id: str
    port: str
    role: str  # "follower" or "leader"
    cameras: dict[str, Any] = field(default_factory=dict)


@dataclass
class DualArmConfig:
    """Configuration for the dual-arm setup."""

    arm_a: ArmConfig
    arm_b: ArmConfig
    leader: ArmConfig | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> DualArmConfig:
        """Load configuration from YAML file.

        Args:
            path: Path to arms.yaml config file.

        Returns:
            DualArmConfig instance.
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        arm_a = ArmConfig(**data["arm_a"])
        arm_b = ArmConfig(**data["arm_b"])
        leader = ArmConfig(**data["leader"]) if "leader" in data else None
        return cls(arm_a=arm_a, arm_b=arm_b, leader=leader)


class DualArmController:
    """Controls two SO-101 follower arms with optional leader for teaching.

    Usage:
        config = DualArmConfig.from_yaml("configs/arms.yaml")
        controller = DualArmController(config)
        controller.connect()
        controller.send_to_well("arm_a", "A1")
        controller.park_all()
        controller.disconnect()
    """

    def __init__(self, config: DualArmConfig) -> None:
        self.config = config
        self._connected = False
        self._stub_mode = False
        self._robots: dict[str, Any] = {}

    @property
    def arm_ids(self) -> list[str]:
        """IDs of configured follower arms."""
        return [
            cfg.arm_id for cfg in [self.config.arm_a, self.config.arm_b] if cfg.role == "follower"
        ]

    def connect(self) -> None:
        """Connect to all configured arms via LeRobot."""
        try:
            from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
        except ImportError:
            logger.warning("lerobot not installed — running in stub mode")
            self._stub_mode = True
            self._connected = True
            return

        for arm_cfg in [self.config.arm_a, self.config.arm_b]:
            if arm_cfg.role != "follower":
                continue
            robot_config = SO101FollowerConfig(
                port=arm_cfg.port,
                id=arm_cfg.arm_id,
                cameras=arm_cfg.cameras,
            )
            robot = SO101Follower(robot_config)
            robot.connect()
            self._robots[arm_cfg.arm_id] = robot
            logger.info("Connected arm %s on %s", arm_cfg.arm_id, arm_cfg.port)

        self._connected = True

    def disconnect(self) -> None:
        """Disconnect all arms."""
        for arm_id, robot in self._robots.items():
            robot.disconnect()
            logger.info("Disconnected arm %s", arm_id)
        self._robots.clear()
        self._connected = False
        self._stub_mode = False

    def get_observation(self, arm_id: str) -> dict[str, Any]:
        """Read current joint positions and camera frames from an arm.

        Args:
            arm_id: Which arm to read from.

        Returns:
            Dict with joint positions and camera data.

        Raises:
            ValueError: If arm_id is not a configured follower arm.
        """
        if self._stub_mode:
            if arm_id not in self.arm_ids:
                raise ValueError(f"Unknown arm: {arm_id}")
            return {"joints": [], "stub": True}
        if arm_id not in self._robots:
            raise ValueError(f"Unknown arm: {arm_id}")
        return self._robots[arm_id].get_observation()

    def send_action(self, arm_id: str, action: Any) -> None:
        """Send a joint-space action to an arm.

        Args:
            arm_id: Which arm to control.
            action: Action tensor (joint positions).

        Raises:
            ValueError: If arm_id is not a configured follower arm.
        """
        if self._stub_mode:
            if arm_id not in self.arm_ids:
                raise ValueError(f"Unknown arm: {arm_id}")
            logger.debug("Stub send_action(%s, %s)", arm_id, action)
            return
        if arm_id not in self._robots:
            raise ValueError(f"Unknown arm: {arm_id}")
        self._robots[arm_id].send_action(action)

    def send_to_well(self, arm_id: str, well_name: str) -> None:
        """Move an arm to a 96-well plate position.

        Args:
            arm_id: Which arm to move.
            well_name: Well name like 'A1', 'H12'.

        Raises:
            ValueError: If well_name is invalid or arm_id unknown.
        """
        well = parse_well_name(well_name)
        logger.info("Moving %s to well %s (%.2f, %.2f mm)", arm_id, well.name, well.x_mm, well.y_mm)
        # Stub: use zero joints. Real IK mapping deferred to MVP.
        stub_joints = [0.0] * 6
        self.send_action(arm_id, stub_joints)

    def park_all(self) -> None:
        """Move all follower arms to the park (safe) position."""
        for arm_id in self.arm_ids:
            logger.info("Parking arm %s", arm_id)
            self.send_action(arm_id, list(PARK_POSITION))
