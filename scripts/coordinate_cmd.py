"""Send coordinate-based commands to an SO-101 arm.

Usage:
    python scripts/coordinate_cmd.py --well A1 --action aspirate
    python scripts/coordinate_cmd.py --well B3 --action dispense
    python scripts/coordinate_cmd.py --park
"""

from __future__ import annotations

import argparse
import logging

from biolab.arms import ArmConfig, DualArmConfig, DualArmController
from biolab.plate import parse_well_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _make_stub_controller() -> DualArmController:
    """Create a stub controller for coordinate testing."""
    config = DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
    )
    ctrl = DualArmController(config)
    ctrl.connect()
    return ctrl


def main() -> None:
    """Parse command and send to arm."""
    parser = argparse.ArgumentParser(description="Coordinate-based arm commands")
    parser.add_argument("--well", help="Target well (e.g., A1, H12)")
    parser.add_argument("--action", choices=["aspirate", "dispense", "move"], default="move")
    parser.add_argument("--volume", type=float, default=100.0, help="Volume in uL")
    parser.add_argument("--park", action="store_true", help="Park arm")
    parser.add_argument("--arm", default="arm_a", help="Which arm to control")
    parser.add_argument("--config", default="configs/arms.yaml", help="Arms config path")
    args = parser.parse_args()

    controller = _make_stub_controller()

    if args.park:
        logger.info("Parking %s", args.arm)
        controller.park_all()
        controller.disconnect()
        return

    if not args.well:
        parser.error("--well is required unless --park is specified")

    well = parse_well_name(args.well)
    logger.info(
        "Target: %s (%.2f, %.2f mm) — action: %s",
        well.name,
        well.x_mm,
        well.y_mm,
        args.action,
    )
    controller.send_to_well(args.arm, args.well)
    controller.disconnect()


if __name__ == "__main__":
    main()
