"""Cartesian motion platform via Klipper/Moonraker HTTP API.

A 3-axis (XYZ) Cartesian motion controller for G-code-based pipetting on a
Voron or similar CoreXY/Cartesian printer running Klipper with Moonraker.
Communicates over HTTP instead of serial, supporting named positions and
graceful stub-mode fallback when the printer is unreachable.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from pathlib import Path

import yaml
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class CartesianConfig(BaseSettings):
    """Configuration for the Cartesian motion platform."""

    model_config = SettingsConfigDict(strict=True)

    moonraker_url: str = "http://localhost:7125"
    timeout_s: float = 10.0
    safe_z_mm: float = 50.0
    approach_z_mm: float = 5.0
    feedrate: int = 3000
    positions: dict[str, tuple[float, float, float]] = {}

    @field_validator("positions", mode="before")
    @classmethod
    def _coerce_positions(cls, v: Any) -> Any:  # noqa: ANN401
        """Coerce YAML lists to tuples for strict mode."""
        if isinstance(v, dict):
            return {k: tuple(val) if isinstance(val, list) else val for k, val in v.items()}
        return v

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load configuration from a YAML file."""
        with open(path) as fh:
            data = yaml.safe_load(fh)
        return cls.model_validate(data)


class CartesianPlatform:
    """Cartesian motion platform via Klipper/Moonraker HTTP API.

    Usage::

        platform = CartesianPlatform(CartesianConfig(positions={"home": (0, 0, 0)}))
        platform.connect()
        platform.home()
        platform.move_to_position("home")
        platform.disconnect()
    """

    def __init__(self, config: CartesianConfig) -> None:
        """Initialize with platform configuration."""
        self.config = config
        self._stub_mode = False
        self._client: Any = None
        self._position: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._gcode_log: list[str] = []

    def connect(self) -> None:
        """Connect to Moonraker HTTP API, falling back to stub mode."""
        try:
            import httpx as _httpx

            self._client = _httpx.Client(
                base_url=self.config.moonraker_url,
                timeout=self.config.timeout_s,
            )
            self._client.get("/server/info")
        except Exception:
            logger.warning("Moonraker unreachable -- running in stub mode")
            self._stub_mode = True
            if self._client is not None:
                self._client.close()
                self._client = None

    def disconnect(self) -> None:
        """Close HTTP client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def send_gcode(self, cmd: str) -> None:
        """Send a G-code command to the printer.

        In stub mode the command is appended to ``_gcode_log`` instead.
        """
        if self._stub_mode:
            self._gcode_log.append(cmd)
            return
        if self._client is not None:
            self._client.post("/api/printer/command", json={"commands": [cmd]})

    def home(self) -> None:
        """Home all axes."""
        self.send_gcode("G28")

    def move_to(self, x: float, y: float, z: float) -> None:
        """Move to an absolute XYZ position.

        Args:
            x: X coordinate in mm.
            y: Y coordinate in mm.
            z: Z coordinate in mm.
        """
        self.send_gcode(self.encode_move(x, y, z, self.config.feedrate))
        self._position = (x, y, z)

    def move_to_position(self, name: str) -> None:
        """Move to a named position from configuration.

        Args:
            name: Position name from ``config.positions``.

        Raises:
            ValueError: If position name is not configured.
        """
        if name not in self.config.positions:
            raise ValueError(f"Unknown position: {name!r}")
        x, y, z = self.config.positions[name]
        self.move_to(x, y, z)

    def raise_to_safe(self) -> None:
        """Raise Z axis to safe travel height, preserving X and Y."""
        self.move_to(self._position[0], self._position[1], self.config.safe_z_mm)

    def get_position(self) -> tuple[float, float, float]:
        """Return current XYZ position.

        In stub mode returns the internally tracked position.
        When connected, queries the printer for live position.
        """
        if self._stub_mode:
            return self._position
        if self._client is not None:
            resp = self._client.post(
                "/printer/objects/query",
                json={"objects": {"toolhead": ["position"]}},
            )
            pos = resp.json()["result"]["status"]["toolhead"]["position"]
            return (pos[0], pos[1], pos[2])
        return self._position

    @property
    def is_stub_mode(self) -> bool:
        """Whether the platform is running in stub mode."""
        return self._stub_mode

    @staticmethod
    def encode_move(x: float, y: float, z: float, feedrate: int) -> str:
        """Encode an absolute move as a G0 G-code command.

        Pure function -- no hardware required, safe to call in tests.

        Args:
            x: X coordinate in mm.
            y: Y coordinate in mm.
            z: Z coordinate in mm.
            feedrate: Travel speed in mm/min.

        Returns:
            G-code string, e.g. ``"G0 X10.000 Y20.000 Z5.000 F3000"``.
        """
        return f"G0 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feedrate}"
