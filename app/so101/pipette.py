"""Pipette control backends for lab automation.

Backends:
- DigitalPipette: DIY syringe + Arduino (https://github.com/ac-rad/digital-pipette-v2)
- ElectronicPipette: Commercial electronic pipettes (AELAB dPette 7016, DLAB dPette+)

Both backends implement PipetteProtocol for interchangeable use in workflows.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class PipetteProtocol(Protocol):
    """Interface that all pipette backends must satisfy."""

    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def aspirate(self, volume_ul: float) -> None: ...
    def dispense(self, volume_ul: float) -> None: ...
    def eject_tip(self) -> None: ...


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
        except Exception as exc:
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


# ---------------------------------------------------------------------------
# Electronic pipette backend (AELAB dPette 7016 / DLAB dPette+)
# ---------------------------------------------------------------------------

# Known models and their default volume ranges
ELECTRONIC_MODELS: dict[str, dict[str, Any]] = {
    "aelab_dpette_7016": {"channels": 1, "max_volume_ul": 1000.0},
    "dlab_dpette_plus": {"channels": 8, "max_volume_ul": 300.0},
}


@dataclass
class ElectronicPipetteConfig:
    """Configuration for a commercial electronic pipette.

    USB protocol is undocumented — the serial_port is a placeholder for
    future reverse-engineering via USBREVue / pyserial.
    """

    serial_port: str = "/dev/ttyACM0"
    baud_rate: int = 9600
    max_volume_ul: float = 1000.0
    channels: int = 1
    model: str = "aelab_dpette_7016"


class ElectronicPipette:
    """Controls a commercial electronic pipette via modular driver loading.

    Driver resolution order:
    1. Try ``import dpette`` (Lambda-Biolab/dpette-usb-driver) — real USB protocol
    2. Fall back to stub mode (volume tracking only, no hardware commands)

    The dpette package is an optional dependency. Install it to enable real
    hardware control; without it, all commands are no-ops and fill state is
    tracked in memory.

    Usage:
        pipette = ElectronicPipette(ElectronicPipetteConfig(model="aelab_dpette_7016"))
        pipette.connect()
        pipette.aspirate(50.0)
        pipette.dispense(50.0)
        pipette.disconnect()
    """

    def __init__(self, config: ElectronicPipetteConfig) -> None:
        self.config = config
        self._driver: Any = None  # dpette.DPetteDriver when available
        self._stub_mode = False
        self._current_fill: float = 0.0

    def connect(self) -> None:
        """Connect to the electronic pipette via modular driver loading.

        Tries to import the ``dpette`` package and create a DPetteDriver.
        Falls back to stub mode if the package or hardware is unavailable.
        """
        try:
            from dpette.config import SerialConfig  # pyright: ignore[reportMissingImports]
            from dpette.driver import DPetteDriver  # pyright: ignore[reportMissingImports]

            cfg = SerialConfig(
                port=self.config.serial_port,
                baudrate=self.config.baud_rate,
            )
            self._driver = DPetteDriver(cfg)
            self._driver.connect()
            logger.info(
                "Electronic pipette (%s) connected via dpette driver on %s",
                self.config.model,
                self.config.serial_port,
            )
        except ImportError:
            logger.warning("dpette package not installed — running in stub mode")
            self._stub_mode = True
        except Exception as exc:
            logger.warning("dpette driver connection failed (%s) — running in stub mode", exc)
            self._stub_mode = True

    def disconnect(self) -> None:
        """Close driver connection."""
        if self._driver:
            self._driver.disconnect()
            self._driver = None

    def aspirate(self, volume_ul: float) -> None:
        """Aspirate a volume of liquid.

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

        if self._driver:
            self._driver.set_volume(volume_ul)
            self._driver.aspirate()
        else:
            logger.debug("Stub mode — skipping aspirate %.1f µL", volume_ul)

        self._current_fill += volume_ul
        logger.info("Aspirated %.1f µL (%s)", volume_ul, self.config.model)

    def dispense(self, volume_ul: float) -> None:
        """Dispense a volume of liquid.

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

        if self._driver:
            self._driver.set_volume(volume_ul)
            self._driver.dispense()
        else:
            logger.debug("Stub mode — skipping dispense %.1f µL", volume_ul)

        self._current_fill -= volume_ul
        logger.info("Dispensed %.1f µL (%s)", volume_ul, self.config.model)

    def eject_tip(self) -> None:
        """Signal tip ejection (mechanical — not sent via driver)."""
        logger.info("Ejecting tip (%s) — mechanical lever", self.config.model)
        if self._driver:
            self._driver.eject_tip()
