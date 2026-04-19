"""Scan a serial port for STS3215 servos.

Useful pre-calibration sanity check: verifies the Waveshare board is reachable
and all expected servos (IDs 1-6 for an SO-101 arm) respond. Reports firmware
versions so mismatches are visible before `lerobot-calibrate` complains.

Usage:
    uv run so101-scan-servos                         # defaults to /dev/ttyACM0
    uv run so101-scan-servos --port=/dev/ttyACM1
    uv run so101-scan-servos --port=/dev/ttyACM0 --id-range=0-20
"""

from __future__ import annotations

import argparse
import sys

BAUD = 1_000_000
ADDR_FIRMWARE_MAJOR = 0
ADDR_FIRMWARE_MINOR = 1


def _parse_range(spec: str) -> range:
    """Parse 'N-M' as inclusive range."""
    lo, hi = spec.split("-")
    return range(int(lo), int(hi) + 1)


def scan(port_path: str, ids: range) -> list[tuple[int, int, str]]:
    """Ping each servo ID; return list of (id, model, firmware) for responders."""
    try:
        from scservo_sdk import PacketHandler, PortHandler  # type: ignore[import-untyped]
    except ImportError as err:
        raise RuntimeError(
            "scservo_sdk not installed — run 'uv sync --group lerobot'"
        ) from err

    port = PortHandler(port_path)
    if not port.openPort():
        raise OSError(f"Cannot open {port_path}")
    port.setBaudRate(BAUD)
    ph = PacketHandler(0)

    found: list[tuple[int, int, str]] = []
    try:
        for sid in ids:
            model, result, _ = ph.ping(port, sid)
            if result != 0:
                continue
            major, _, _ = ph.read1ByteTxRx(port, sid, ADDR_FIRMWARE_MAJOR)
            minor, _, _ = ph.read1ByteTxRx(port, sid, ADDR_FIRMWARE_MINOR)
            found.append((sid, model, f"{major}.{minor}"))
    finally:
        port.closePort()

    return found


def main() -> None:
    """CLI entry point for servo scan."""
    parser = argparse.ArgumentParser(description="Scan serial port for STS3215 servos")
    parser.add_argument(
        "--port", default="/dev/ttyACM0", help="serial port (default: /dev/ttyACM0)"
    )
    parser.add_argument(
        "--id-range", default="1-20", help="servo ID range to probe (default: 1-20)"
    )
    args = parser.parse_args()

    try:
        found = scan(args.port, _parse_range(args.id_range))
    except OSError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if not found:
        print(f"No servos found on {args.port}. Check power supply and cable.")
        sys.exit(2)

    print(f"Found {len(found)} servo(s) on {args.port}:")
    firmwares = {fw for _, _, fw in found}
    for sid, model, fw in found:
        print(f"  ID {sid:>3}  model={model}  firmware={fw}")

    if len(firmwares) > 1:
        print(
            f"\nWARNING: mixed firmware versions {sorted(firmwares)}. "
            "Run 'make patch_lerobot' before calibration.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
