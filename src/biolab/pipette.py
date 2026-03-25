"""Digital pipette control via Arduino serial interface.

Reference: https://github.com/ac-rad/digital-pipette-v2
Controls a linear actuator to aspirate/dispense liquid through a syringe-based pipette.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Actuator positions (0-1023 range for 5cm stroke linear actuator)
ACTUATOR_MIN = 0  # Fully retracted (max suction)
ACTUATOR_MAX = 1023  # Fully extended (no suction)
DEFAULT_ASPIRATE_SPEED = 200  # ms delay between steps
DEFAULT_DISPENSE_SPEED = 150  # ms delay between steps


@dataclass
class PipetteConfig:
    """Configuration for the digital pipette."""

    serial_port: str = "/dev/ttyUSB0"
    baud_rate: int = 9600
    max_volume_ul: float = 200.0
    actuator_stroke_mm: float = 50.0


class DigitalPipette:
    """Controls the digital pipette v2 via Arduino serial.

    Usage:
        pipette = DigitalPipette(PipetteConfig(serial_port="/dev/ttyUSB0"))
        pipette.connect()
        pipette.aspirate(100.0)  # Aspirate 100 µL
        pipette.dispense(100.0)  # Dispense 100 µL
        pipette.disconnect()
    """

    def __init__(self, config: PipetteConfig) -> None:
        self.config = config
        self._serial = None
        self._current_position = ACTUATOR_MAX  # Start fully extended (empty)
        self._current_fill: float = 0.0  # Tracked in µL

    def connect(self) -> None:
        """Open serial connection to Arduino controller."""
        try:
            import serial

            self._serial = serial.Serial(
                self.config.serial_port,
                self.config.baud_rate,
                timeout=2,
            )
            time.sleep(2)  # Wait for Arduino reset
            logger.info("Pipette connected on %s", self.config.serial_port)
        except ImportError:
            logger.warning("pyserial not installed — running in stub mode")
        except Exception as exc:  # noqa: BLE001
            # Reason: SerialException (port missing/inaccessible) degrades to stub mode
            logger.warning("Serial connection failed (%s) — running in stub mode", exc)

    def disconnect(self) -> None:
        """Close serial connection."""
        if self._serial:
            self._serial.close()
            self._serial = None

    def _volume_to_steps(self, volume_ul: float) -> int:
        """Convert volume in µL to actuator step count.

        Args:
            volume_ul: Volume in microliters.

        Returns:
            Number of actuator steps.
        """
        fraction = volume_ul / self.config.max_volume_ul
        return int(fraction * ACTUATOR_MAX)

    def aspirate(self, volume_ul: float) -> None:
        """Aspirate (draw up) a volume of liquid.

        Args:
            volume_ul: Volume to aspirate in microliters.

        Raises:
            ValueError: If volume exceeds capacity.
        """
        if volume_ul <= 0:
            raise ValueError("Volume must be positive")
        if volume_ul > self.config.max_volume_ul:
            raise ValueError(f"Volume {volume_ul} µL exceeds max {self.config.max_volume_ul} µL")
        if self._current_fill + volume_ul > self.config.max_volume_ul:
            raise ValueError(
                f"Cannot aspirate {volume_ul} µL: would exceed capacity "
                f"(current fill {self._current_fill} µL, max {self.config.max_volume_ul} µL)"
            )

        steps = self._volume_to_steps(volume_ul)
        target = max(self._current_position - steps, ACTUATOR_MIN)
        self._move_to(target)
        self._current_fill += volume_ul
        logger.info("Aspirated %.1f µL (position: %d)", volume_ul, self._current_position)

    def dispense(self, volume_ul: float) -> None:
        """Dispense (push out) a volume of liquid.

        Args:
            volume_ul: Volume to dispense in microliters.

        Raises:
            ValueError: If volume exceeds current contents.
        """
        if volume_ul <= 0:
            raise ValueError("Volume must be positive")
        if volume_ul > self._current_fill:
            raise ValueError(
                f"Cannot dispense {volume_ul} µL: exceeds current fill of {self._current_fill} µL"
            )

        steps = self._volume_to_steps(volume_ul)
        target = min(self._current_position + steps, ACTUATOR_MAX)
        self._move_to(target)
        self._current_fill -= volume_ul
        logger.info("Dispensed %.1f µL (position: %d)", volume_ul, self._current_position)

    def eject_tip(self) -> None:
        """Signal tip ejection (move to eject position then return)."""
        logger.info("Ejecting tip")
        if self._serial:
            self._serial.write(b"EJECT\n")

    def _move_to(self, position: int) -> None:
        """Move actuator to target position.

        Args:
            position: Target position (0-1023).
        """
        if self._serial:
            cmd = f"MOVE {position}\n"
            self._serial.write(cmd.encode())
            self._serial.readline()  # Wait for ACK
        self._current_position = position
