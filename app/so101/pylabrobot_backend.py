"""PyLabRobot-compatible backend for SO-101 dual robotic arms.

Wraps the existing DualArmController + PipetteProtocol so SO-101 arms
can be used via the PyLabRobot ecosystem. Falls back to a standalone
class when pylabrobot is not installed.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from so101.arms import DualArmController
    from so101.pipette import PipetteProtocol

logger = logging.getLogger(__name__)


class SO101BackendConfig(BaseModel):
    """Configuration for the SO-101 PyLabRobot backend."""

    model_config = ConfigDict(strict=True)

    arm_id: str = "arm_a"
    pipette_backend: str = "digital_pipette_v2"


def _get_base_class() -> type:
    """Return MachineBackend if pylabrobot is installed, else object."""
    try:
        from pylabrobot.machine import MachineBackend  # pyright: ignore[reportMissingImports]

        return MachineBackend  # pyright: ignore[reportReturnType]
    except ImportError:
        return object


class SO101Backend(_get_base_class()):
    """PyLabRobot backend for SO-101 dual robotic arms.

    When pylabrobot is installed, inherits from MachineBackend.
    Otherwise, provides the same async interface as a standalone class.
    """

    def __init__(
        self,
        config: SO101BackendConfig,
        arm: DualArmController,
        pipette: PipetteProtocol,
    ) -> None:
        """Initialize with config, arm controller, and pipette.

        Args:
            config: Backend configuration.
            arm: Dual arm controller instance.
            pipette: Pipette backend satisfying PipetteProtocol.
        """
        self.config = config
        self._arm = arm
        self._pipette = pipette
        self._stub_mode = False

    async def setup(self) -> None:
        """Initialize backend (MachineBackend interface)."""
        if not self._arm.is_connected:
            self._arm.connect()
        self._pipette.connect()

    async def stop(self) -> None:
        """Shutdown backend (MachineBackend interface)."""
        self._pipette.disconnect()

    async def aspirate(self, volume_ul: float) -> None:
        """Aspirate via the attached pipette.

        Args:
            volume_ul: Volume to aspirate in microliters.

        Raises:
            ValueError: If volume exceeds pipette capacity.
        """
        self._pipette.aspirate(volume_ul)

    async def dispense(self, volume_ul: float) -> None:
        """Dispense via the attached pipette.

        Args:
            volume_ul: Volume to dispense in microliters.

        Raises:
            ValueError: If volume exceeds current fill.
        """
        self._pipette.dispense(volume_ul)

    async def pick_up_tip(self) -> None:
        """Placeholder for tip pickup."""

    async def drop_tip(self) -> None:
        """Eject tip via pipette."""
        self._pipette.eject_tip()

    async def move_to(self, arm_id: str, position: list[float]) -> None:
        """Move arm to joint position.

        Args:
            arm_id: Which arm to control.
            position: Target joint positions.

        Raises:
            ValueError: If arm_id is not a configured follower arm.
        """
        self._arm.send_action(arm_id, position)

    @property
    def is_stub_mode(self) -> bool:
        """Whether the arm controller is running in stub mode."""
        return self._arm.is_stub_mode
