"""XZ gantry controller for dedicated pipetting arm.

A minimal 2-axis (X horizontal, Z vertical) motion controller for moving a
fixed-mount pipette between named positions. Much simpler than a 6-DOF arm
— suitable for repetitive pipetting at 2-3 fixed positions.

Supported controllers: Pololu Maestro (USB servo), Raspberry Pi Pico W.
"""

from __future__ import annotations

import logging
import struct
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class XZGantryConfig:
    """Configuration for the XZ gantry."""

    serial_port: str = "/dev/ttyUSB1"
    baud_rate: int = 115200
    controller: str = "pololu_maestro"  # or "pico_w"
    x_range_mm: float = 200.0
    z_range_mm: float = 100.0
    safe_z_mm: float = 80.0
    approach_z_mm: float = 20.0
    positions: dict[str, tuple[float, float]] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str) -> XZGantryConfig:
        """Load configuration from a YAML file."""
        import yaml

        with open(path) as fh:
            data = yaml.safe_load(fh)
        positions = {k: tuple(v) for k, v in data.get("positions", {}).items()}
        return cls(
            serial_port=data.get("serial_port", "/dev/ttyUSB1"),
            baud_rate=data.get("baud_rate", 115200),
            controller=data.get("controller", "pololu_maestro"),
            x_range_mm=data.get("x_range_mm", 200.0),
            z_range_mm=data.get("z_range_mm", 100.0),
            safe_z_mm=data.get("safe_z_mm", 80.0),
            approach_z_mm=data.get("approach_z_mm", 20.0),
            positions=positions,
        )


class XZGantry:
    """Controls a 2-axis XZ gantry for dedicated pipetting.

    Usage:
        gantry = XZGantry(XZGantryConfig(positions={"trough": (0, 0), "plate": (45, 11)}))
        gantry.connect()
        gantry.move_to_position("trough")
        gantry.lower()
        # ... pipette aspirate ...
        gantry.raise_z()
        gantry.move_to_position("plate")
        gantry.disconnect()
    """

    def __init__(self, config: XZGantryConfig) -> None:
        self.config = config
        self._serial: Any = None
        self._stub_mode = False
        self._current_x: float = 0.0
        self._current_z: float = config.safe_z_mm

    def connect(self) -> None:
        """Open serial connection to the gantry controller."""
        try:
            import serial

            self._serial = serial.Serial(
                self.config.serial_port,
                self.config.baud_rate,
                timeout=2,
            )
            logger.info("XZ gantry connected on %s", self.config.serial_port)
        except ImportError:
            logger.warning("pyserial not installed — running in stub mode")
            self._stub_mode = True
        except Exception as exc:
            logger.warning("Serial connection failed (%s) — running in stub mode", exc)
            self._stub_mode = True

    def disconnect(self) -> None:
        """Close serial connection."""
        if self._serial:
            self._serial.close()
            self._serial = None

    def move_to_position(self, name: str) -> None:
        """Move X axis to a named position.

        Args:
            name: Position name from config.positions.

        Raises:
            ValueError: If position name is not configured.
        """
        if name not in self.config.positions:
            raise ValueError(f"Unknown position: {name!r}")

        x, _y = self.config.positions[name]
        self._send_command(f"MOVE_X {x}")
        self._current_x = x
        logger.info("Moved to position %r (x=%.1f mm)", name, x)

    def lower(self) -> None:
        """Lower Z axis to approach height."""
        self._send_command(f"MOVE_Z {self.config.approach_z_mm}")
        self._current_z = self.config.approach_z_mm
        logger.info("Lowered to z=%.1f mm", self._current_z)

    def raise_z(self) -> None:
        """Raise Z axis to safe travel height."""
        self._send_command(f"MOVE_Z {self.config.safe_z_mm}")
        self._current_z = self.config.safe_z_mm
        logger.info("Raised to z=%.1f mm", self._current_z)

    def teach_position(self, name: str) -> None:
        """Save current X/Z as a named position.

        Args:
            name: Position name to save.
        """
        self.config.positions[name] = (self._current_x, self._current_z)
        logger.info("Taught position %r = (%.1f, %.1f)", name, self._current_x, self._current_z)

    def save_config(self, path: str) -> None:
        """Write current configuration (including taught positions) to YAML.

        Args:
            path: Output YAML file path.
        """
        import yaml

        data = {
            "serial_port": self.config.serial_port,
            "baud_rate": self.config.baud_rate,
            "controller": self.config.controller,
            "x_range_mm": self.config.x_range_mm,
            "z_range_mm": self.config.z_range_mm,
            "safe_z_mm": self.config.safe_z_mm,
            "approach_z_mm": self.config.approach_z_mm,
            "positions": {k: list(v) for k, v in self.config.positions.items()},
        }
        with open(path, "w") as fh:
            yaml.safe_dump(data, fh, default_flow_style=False)
        logger.info("Config saved to %s", path)

    def _send_command(self, cmd: str) -> None:
        """Send a command via the configured controller protocol."""
        if self._serial:
            if self.config.controller == "pololu_maestro":
                self._send_maestro(cmd)
            else:
                self._send_pico(cmd)
        else:
            logger.debug("Stub mode — skipping command: %s", cmd)

    @staticmethod
    def encode_maestro(cmd: str, x_range_mm: float, z_range_mm: float) -> bytes:
        """Encode a MOVE_X/MOVE_Z command into Pololu Maestro wire bytes.

        Protocol: 0x84, channel, target_low_bits, target_high_bits.
        Channel 0 = X axis servo, Channel 1 = Z axis servo.
        Target is in quarter-microseconds (e.g., 6000 = 1500µs center).
        Map mm to servo pulse (quarter-microseconds): 1000-2000µs → 4000-8000 qµs.

        Pure function — no hardware required, safe to call in tests.
        """
        parts = cmd.split()
        channel = 0 if "X" in parts[0] else 1
        value_mm = float(parts[1])
        axis_range = x_range_mm if channel == 0 else z_range_mm
        fraction = max(0.0, min(1.0, value_mm / axis_range)) if axis_range > 0 else 0.0
        target = int(4000 + fraction * 4000)  # 4000-8000 range
        return struct.pack("<BBH", 0x84, channel, target)

    @staticmethod
    def encode_pico(cmd: str) -> bytes:
        """Encode a command as plain text for Pico W over USB serial.

        Pure function — no hardware required, safe to call in tests.
        """
        return f"{cmd}\n".encode()

    def _send_maestro(self, cmd: str) -> None:
        """Send command using Pololu Maestro compact binary protocol."""
        data = self.encode_maestro(cmd, self.config.x_range_mm, self.config.z_range_mm)
        self._serial.write(data)

    def _send_pico(self, cmd: str) -> None:
        """Send command as plain text to Pico W over USB serial."""
        self._serial.write(self.encode_pico(cmd))
        self._serial.readline()
