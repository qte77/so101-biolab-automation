"""End-to-end demo orchestrator for so101-biolab-automation.

Usage:
    python scripts/run_demo.py                          # full demo (all use cases)
    python scripts/run_demo.py --use-case uc1_single --well A1 --volume 50
    python scripts/run_demo.py --use-case uc1_row --row A
    python scripts/run_demo.py --use-case uc1_col --col 1
    python scripts/run_demo.py --use-case uc1_full
    python scripts/run_demo.py --use-case uc2
    python scripts/run_demo.py --use-case uc3
"""

from __future__ import annotations

import argparse
import logging

from biolab.workflow import (
    create_workflow_context,
    uc1_col,
    uc1_full_plate,
    uc1_row,
    uc1_single_well,
    uc2_fridge_open_grab_move,
    uc3_tool_cycle,
    uc4_demo_all,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

USE_CASES = ["all", "uc1_single", "uc1_row", "uc1_col", "uc1_full", "uc2", "uc3"]


def main() -> None:
    """Run the demo orchestrator."""
    parser = argparse.ArgumentParser(description="so101-biolab-automation demo")
    parser.add_argument("--use-case", choices=USE_CASES, default="all")
    parser.add_argument("--mode", choices=["full", "eval", "teleop"], default="full")
    parser.add_argument("--well", default="A1", help="Target well for uc1_single")
    parser.add_argument("--row", default="A", help="Target row for uc1_row")
    parser.add_argument("--col", type=int, default=1, help="Target column for uc1_col")
    parser.add_argument("--volume", type=float, default=50.0, help="Volume in µL")
    parser.add_argument("--arm", default="arm_a", help="Which arm to use")
    args = parser.parse_args()

    logger.info("Starting demo: use_case=%s", args.use_case)

    arm, pipette, changer, layout = create_workflow_context()

    try:
        if args.use_case == "all" or args.mode == "full":
            uc4_demo_all(arm, pipette, changer, layout, args.arm)
        elif args.use_case == "uc1_single":
            uc1_single_well(arm, pipette, layout, args.arm, args.well, args.volume)
        elif args.use_case == "uc1_row":
            uc1_row(arm, pipette, layout, args.arm, args.row, args.volume)
        elif args.use_case == "uc1_col":
            uc1_col(arm, pipette, layout, args.arm, args.col, args.volume)
        elif args.use_case == "uc1_full":
            uc1_full_plate(arm, pipette, layout, args.arm, args.volume)
        elif args.use_case == "uc2":
            uc2_fridge_open_grab_move(arm, changer, args.arm)
        elif args.use_case == "uc3":
            uc3_tool_cycle(arm, changer, args.arm)
    finally:
        arm.disconnect()

    logger.info("Demo complete.")


if __name__ == "__main__":
    main()
