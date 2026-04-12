"""Safety systems: e-stop, watchdog, joint limits.

Ensures arms park safely on connection loss or error conditions.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# SO-101 joint limits (degrees) — conservative defaults
JOINT_LIMITS = {
    "shoulder_pan": (-150.0, 150.0),
    "shoulder_lift": (-90.0, 90.0),
    "elbow_flex": (-120.0, 120.0),
    "wrist_flex": (-100.0, 100.0),
    "wrist_roll": (-150.0, 150.0),
    "gripper": (-10.0, 70.0),
}

# Park position: arms folded up safely
PARK_POSITION = [0.0, -45.0, -90.0, 0.0, 0.0, 0.0]


class SafetyConfig(BaseModel):
    """Safety system configuration."""

    model_config = ConfigDict(strict=True)

    watchdog_timeout_s: float = 5.0
    heartbeat_interval_s: float = 1.0
    joint_limits: dict[str, tuple[float, float]] = Field(default_factory=lambda: dict(JOINT_LIMITS))


class SafetyMonitor:
    """Monitors arm safety and triggers emergency stop on violations.

    Usage:
        monitor = SafetyMonitor(config, park_callback=controller.park_all)
        monitor.start()
        monitor.heartbeat()  # Call regularly from remote client
        monitor.stop()
    """

    def __init__(self, config: SafetyConfig, park_callback: Callable[[], None]) -> None:
        """Initialize with safety config and park callback."""
        self.config = config
        self._park = park_callback
        self._last_heartbeat = time.monotonic()
        self._stopped = False
        self._e_stopped = False
        self._watchdog_thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the watchdog timer."""
        self._stopped = False
        self._last_heartbeat = time.monotonic()
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog_thread.start()
        logger.info("Safety monitor started (timeout=%.1fs)", self.config.watchdog_timeout_s)

    def stop(self) -> None:
        """Stop the watchdog timer."""
        self._stopped = True
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=2.0)
        logger.info("Safety monitor stopped")

    def heartbeat(self) -> None:
        """Reset the watchdog timer. Call from remote client at regular intervals."""
        self._last_heartbeat = time.monotonic()

    def e_stop(self) -> None:
        """Trigger emergency stop — park all arms immediately."""
        logger.warning("E-STOP triggered")
        self._e_stopped = True
        self._park()

    def reset_e_stop(self) -> None:
        """Reset e-stop state (requires explicit operator action)."""
        self._e_stopped = False
        logger.info("E-STOP reset")

    @property
    def is_e_stopped(self) -> bool:
        """Whether e-stop is currently active."""
        return self._e_stopped

    def check_joint_limits(self, joint_name: str, value: float) -> bool:
        """Check if a joint value is within safe limits.

        Args:
            joint_name: Name of the joint.
            value: Joint angle in degrees.

        Returns:
            True if within limits, False if violated.
        """
        if joint_name not in self.config.joint_limits:
            return True
        lo, hi = self.config.joint_limits[joint_name]
        if value < lo or value > hi:
            logger.warning(
                "Joint limit violation: %s=%.1f (limits: %.1f-%.1f)", joint_name, value, lo, hi
            )
            return False
        return True

    def _check_watchdog(self) -> None:
        """Run one watchdog check — park and e-stop if heartbeat is overdue.

        Extracted so tests can drive the watchdog logic deterministically
        without starting the polling thread.
        """
        elapsed = time.monotonic() - self._last_heartbeat
        if elapsed > self.config.watchdog_timeout_s and not self._e_stopped:
            logger.warning("Watchdog timeout (%.1fs) — parking arms", elapsed)
            self._park()
            self._e_stopped = True

    def _watchdog_loop(self) -> None:
        """Background thread checking for heartbeat timeout."""
        while not self._stopped:
            self._check_watchdog()
            time.sleep(0.5)
