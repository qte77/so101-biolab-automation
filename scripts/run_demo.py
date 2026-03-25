"""End-to-end demo orchestrator for so101-biolab-duo.

Runs the full demo workflow:
1. Connect arms
2. Change tools as needed
3. Execute pipetting or pick-and-place tasks
4. Stream status to dashboard
"""

from __future__ import annotations

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the demo orchestrator."""
    parser = argparse.ArgumentParser(description="so101-biolab-duo demo")
    parser.add_argument("--mode", choices=["full", "eval", "teleop"], default="full")
    parser.add_argument("--arm-port", default="/dev/ttyACM1")
    parser.add_argument("--config", default="configs/arms.yaml")
    args = parser.parse_args()

    logger.info("Starting demo in %s mode", args.mode)
    logger.info("Config: %s", args.config)

    # TODO: Wire up arm controller, tool changer, pipette, and dashboard
    # This is the Phase 5 integration point
    logger.info("Demo scaffold — implement in Phase 5")


if __name__ == "__main__":
    main()
