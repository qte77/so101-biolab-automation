#!/usr/bin/env python3
"""Patch lerobot to tolerate mixed STS3215 firmware versions.

STS3215 servos may ship with mixed firmware versions (e.g. 3.9 and 3.10).
LeRobot 0.4.4 has two problems with this:

1. _assert_same_firmware() raises RuntimeError if versions differ
2. sync_read fails with "Incorrect status packet!" because firmware 3.9
   returns a slightly different packet format, corrupting the batch response

This script patches the installed lerobot package in-place:
- Firmware check: warn instead of raise
- sync_read: fall back to sequential individual reads on failure

Re-run after `uv sync` reinstalls lerobot.

Usage:
    uv run so101-patch-lerobot           # apply both patches
    uv run so101-patch-lerobot --revert  # restore originals
"""

from __future__ import annotations

import sys
from pathlib import Path

SITE_PACKAGES = Path(
    sys.prefix,
    "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages",
    "lerobot",
    "motors",
)

FEETECH_PY = SITE_PACKAGES / "feetech" / "feetech.py"
MOTORS_BUS_PY = SITE_PACKAGES / "motors_bus.py"

# --- Patch 1: firmware version check ---

FW_ORIGINAL = '''\
    def _assert_same_firmware(self) -> None:
        firmware_versions = self._read_firmware_version(self.ids, raise_on_error=True)
        if len(set(firmware_versions.values())) != 1:
            raise RuntimeError(
                "Some Motors use different firmware versions:"
                f"\\n{pformat(firmware_versions)}\\n"
                "Update their firmware first using Feetech's software. "
                "Visit https://www.feetechrc.com/software."
            )'''

FW_PATCHED = '''\
    def _assert_same_firmware(self) -> None:
        firmware_versions = self._read_firmware_version(self.ids, raise_on_error=True)
        if len(set(firmware_versions.values())) != 1:
            import logging
            logging.getLogger("lerobot.motors.feetech").warning(
                "Mixed firmware versions detected (PATCHED — continuing anyway):"
                f"\\n{pformat(firmware_versions)}\\n"
                "For production use, update firmware via Feetech FD software."
            )'''

# --- Patch 2: sync_read fallback to sequential reads ---

SYNC_ORIGINAL = '''\
    def _sync_read(
        self,
        addr: int,
        length: int,
        motor_ids: list[int],
        *,
        num_retry: int = 0,
        raise_on_error: bool = True,
        err_msg: str = "",
    ) -> tuple[dict[int, int], int]:
        self._setup_sync_reader(motor_ids, addr, length)
        for n_try in range(1 + num_retry):
            comm = self.sync_reader.txRxPacket()
            if self._is_comm_success(comm):
                break
            logger.debug(
                f"Failed to sync read @{addr=} ({length=}) on {motor_ids=} ({n_try=}): "
                + self.packet_handler.getTxRxResult(comm)
            )

        if not self._is_comm_success(comm) and raise_on_error:
            raise ConnectionError(f"{err_msg} {self.packet_handler.getTxRxResult(comm)}")

        values = {id_: self.sync_reader.getData(id_, addr, length) for id_ in motor_ids}
        return values, comm'''

SYNC_PATCHED = '''\
    _sync_read_warned = False  # PATCHED: suppress repeated warnings

    def _sync_read(
        self,
        addr: int,
        length: int,
        motor_ids: list[int],
        *,
        num_retry: int = 0,
        raise_on_error: bool = True,
        err_msg: str = "",
    ) -> tuple[dict[int, int], int]:
        self._setup_sync_reader(motor_ids, addr, length)
        for n_try in range(1 + num_retry):
            comm = self.sync_reader.txRxPacket()
            if self._is_comm_success(comm):
                break
            logger.debug(
                f"Failed to sync read @{addr=} ({length=}) on {motor_ids=} ({n_try=}): "
                + self.packet_handler.getTxRxResult(comm)
            )

        if self._is_comm_success(comm):
            values = {id_: self.sync_reader.getData(id_, addr, length) for id_ in motor_ids}
            return values, comm

        # PATCHED: fall back to sequential individual reads (mixed firmware workaround)
        if not self._sync_read_warned:
            logger.warning(
                f"sync_read failed on {motor_ids=}, using sequential reads "
                "(mixed firmware workaround, this message shown once)"
            )
            self._sync_read_warned = True
        values = {}
        last_comm = comm
        for motor_id in motor_ids:
            val, c, error = self._read(
                addr, length, motor_id, num_retry=num_retry, raise_on_error=False
            )
            if self._is_error(error):
                logger.debug(
                    f"Transient servo error on {motor_id=}: "
                    + self.packet_handler.getRxPacketError(error)
                )
            # Clamp to valid STS3215 range (0-4095) — glitchy reads can return negatives
            val = max(0, min(4095, val))
            values[motor_id] = val
            last_comm = c
        return values, last_comm'''


# --- Patch 3: clamp calibration range values before writing to servo EPROM ---

CAL_ORIGINAL = '''\
    def write_calibration(self, calibration_dict: dict[str, MotorCalibration], cache: bool = True) -> None:
        for motor, calibration in calibration_dict.items():
            if self.protocol_version == 0:
                self.write("Homing_Offset", motor, calibration.homing_offset)
            self.write("Min_Position_Limit", motor, calibration.range_min)
            self.write("Max_Position_Limit", motor, calibration.range_max)'''

CAL_PATCHED = '''\
    def write_calibration(self, calibration_dict: dict[str, MotorCalibration], cache: bool = True) -> None:
        for motor, calibration in calibration_dict.items():
            if self.protocol_version == 0:
                self.write("Homing_Offset", motor, calibration.homing_offset)
            # PATCHED: clamp to valid range — glitchy reads can produce negatives
            range_min = max(0, min(4095, calibration.range_min))
            range_max = max(0, min(4095, calibration.range_max))
            self.write("Min_Position_Limit", motor, range_min)
            self.write("Max_Position_Limit", motor, range_max)'''


def _apply_patch(path: Path, original: str, patched: str, name: str, *, revert: bool) -> bool:
    """Apply or revert a single patch. Returns True if a change was made."""
    if not path.exists():
        print(f"  SKIP {name}: {path} not found")
        return False

    source = path.read_text()

    if revert:
        if patched not in source:
            print(f"  SKIP {name}: patch not applied")
            return False
        path.write_text(source.replace(patched, original))
        print(f"  REVERTED {name}: {path}")
        return True

    if patched in source:
        print(f"  SKIP {name}: already patched")
        return False
    if original not in source:
        print(f"  ERROR {name}: expected code not found (lerobot version may differ)")
        return False
    path.write_text(source.replace(original, patched))
    print(f"  PATCHED {name}: {path}")
    return True


def main() -> None:
    """Apply or revert lerobot patches based on CLI flags."""
    revert = "--revert" in sys.argv
    action = "Reverting" if revert else "Applying"
    print(f"{action} lerobot patches for mixed firmware workaround...")

    results = [
        _apply_patch(FEETECH_PY, FW_ORIGINAL, FW_PATCHED, "firmware_check", revert=revert),
        _apply_patch(MOTORS_BUS_PY, SYNC_ORIGINAL, SYNC_PATCHED, "sync_read_fallback", revert=revert),
        _apply_patch(FEETECH_PY, CAL_ORIGINAL, CAL_PATCHED, "calibration_clamp", revert=revert),
    ]

    if not any(results):
        print("No changes made.")
    else:
        print("Done. Re-run after `uv sync` reinstalls lerobot.")


if __name__ == "__main__":
    main()
