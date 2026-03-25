"""Send coordinate-based commands to an SO-101 arm.

Usage:
    python scripts/coordinate_cmd.py --well A1 --action aspirate
    python scripts/coordinate_cmd.py --well B3 --action dispense
    python scripts/coordinate_cmd.py --park
"""

from __future__ import annotations

import argparse
import logging
import sys

sys.path.insert(0, "src")

from biolab.plate import parse_well_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Parse command and send to arm."""
    parser = argparse.ArgumentParser(description="Coordinate-based arm commands")
    parser.add_argument("--well", help="Target well (e.g., A1, H12)")
    parser.add_argument("--action", choices=["aspirate", "dispense", "move"], default="move")
    parser.add_argument("--volume", type=float, default=100.0, help="Volume in µL")
    parser.add_argument("--park", action="store_true", help="Park arm")
    parser.add_argument("--arm", default="arm_a", help="Which arm to control")
    args = parser.parse_args()

    if args.park:
        logger.info("Parking %s", args.arm)
        # TODO: Send park position to arm
        return

    if not args.well:
        parser.error("--well is required unless --park is specified")

    well = parse_well_name(args.well)
    logger.info("Target: %s (%.2f, %.2f mm) — action: %s",
                well.name, well.x_mm, well.y_mm, args.action)

    # TODO: Convert well coordinates to arm joint space and send
    # This requires plate origin calibration from configs/plate_layout.yaml


if __name__ == "__main__":
    main()
