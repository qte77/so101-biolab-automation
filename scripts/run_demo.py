"""End-to-end demo orchestrator for so101-biolab-automation.

Runs the full demo workflow:
1. Connect arms
2. Change tools as needed
3. Execute pipetting or pick-and-place tasks
4. Stream status to dashboard
"""

from __future__ import annotations

import argparse
import logging

from biolab.arms import ArmConfig, DualArmConfig, DualArmController
from biolab.safety import SafetyConfig, SafetyMonitor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the demo orchestrator."""
    parser = argparse.ArgumentParser(description="so101-biolab-automation demo")
    parser.add_argument("--mode", choices=["full", "eval", "teleop"], default="full")
    parser.add_argument("--arm-port", default="/dev/ttyACM1")
    parser.add_argument("--config", default="configs/arms.yaml")
    args = parser.parse_args()

    logger.info("Starting demo in %s mode", args.mode)

    config = DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port=args.arm_port, role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/ttyACM2", role="follower"),
    )
    controller = DualArmController(config)
    controller.connect()

    monitor = SafetyMonitor(SafetyConfig(), park_callback=controller.park_all)
    monitor.start()

    logger.info("Arms connected (stub mode). Monitor active.")
    logger.info("Demo pipeline: mode=%s — real IK deferred to MVP", args.mode)

    monitor.stop()
    controller.disconnect()
    logger.info("Demo complete.")


if __name__ == "__main__":
    main()
