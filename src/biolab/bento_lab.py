"""Bento Lab portable PCR thermocycler control.

The Bento Lab combines a centrifuge, thermocycler, and gel electrophoresis unit.
Control interface is TBD — this module runs in stub mode until the serial/USB
protocol is determined (same approach as ElectronicPipette).

Reference: https://www.bento.bio/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BentoLabConfig:
    """Configuration for the Bento Lab."""

    serial_port: str = "/dev/ttyACM0"
    baud_rate: int = 9600
    model: str = "bento_lab_standard"


class BentoLab:
    """Controls the Bento Lab portable PCR machine.

    Usage:
        lab = BentoLab(BentoLabConfig())
        lab.connect()
        lab.close_lid()
        lab.start_program("pcr_standard")
        status = lab.get_status()
        lab.disconnect()
    """

    def __init__(self, config: BentoLabConfig) -> None:
        self.config = config
        self._serial: Any = None
        self._stub_mode = False
        self._lid_open = False
        self._running = False
        self._current_program: str | None = None

    def connect(self) -> None:
        """Open serial connection to the Bento Lab."""
        try:
            import serial

            self._serial = serial.Serial(
                self.config.serial_port,
                self.config.baud_rate,
                timeout=2,
            )
            logger.info("Bento Lab connected on %s", self.config.serial_port)
        except ImportError:
            logger.warning("pyserial not installed — running in stub mode")
            self._stub_mode = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Serial connection failed (%s) — running in stub mode", exc)
            self._stub_mode = True

    def disconnect(self) -> None:
        """Close serial connection."""
        if self._serial:
            self._serial.close()
            self._serial = None

    def open_lid(self) -> None:
        """Open the thermocycler lid."""
        self._send_command("LID_OPEN")
        self._lid_open = True
        logger.info("Lid opened")

    def close_lid(self) -> None:
        """Close the thermocycler lid."""
        self._send_command("LID_CLOSE")
        self._lid_open = False
        logger.info("Lid closed")

    def start_program(self, name: str) -> None:
        """Start a PCR program.

        Args:
            name: Program name (must match a configured program).

        Raises:
            ValueError: If lid is open.
        """
        if self._lid_open:
            raise ValueError("Cannot start program: lid must be closed")
        self._send_command(f"RUN {name}")
        self._running = True
        self._current_program = name
        logger.info("Started program: %s", name)

    def get_status(self) -> dict[str, Any]:
        """Return current instrument status."""
        return {
            "lid_open": self._lid_open,
            "running": self._running,
            "program": self._current_program,
            "model": self.config.model,
        }

    def _send_command(self, cmd: str) -> None:
        """Send a command over serial (no-op in stub mode)."""
        if self._serial:
            self._serial.write(f"{cmd}\n".encode())
            self._serial.readline()
        else:
            logger.debug("Stub mode — skipping command: %s", cmd)
