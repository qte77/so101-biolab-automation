"""Workflow orchestration — E2E use cases composing existing modules.

Use cases:
- UC1: Pipette a 96-well plate (single, row, column, full)
- UC2: Open fridge, grab item, move out
- UC3: Tool interchange cycle
- UC4: Demo mode (all use cases in sequence)
- UC5: Gantry-based pipetting (XZ gantry + any PipetteProtocol backend)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from biolab.arms import DualArmConfig, DualArmController
from biolab.pipette import (
    DigitalPipette,
    ElectronicPipette,
    ElectronicPipetteConfig,
    PipetteConfig,
    PipetteProtocol,
)
from biolab.plate import ROWS, all_wells, parse_well_name
from biolab.tool_changer import Tool, ToolChanger, ToolDockConfig

logger = logging.getLogger(__name__)

# Fridge operation joint arrays (stub values — calibrate with real hardware)
FRIDGE_APPROACH_JOINTS = [45.0, -20.0, -40.0, 0.0, 0.0, 30.0]
FRIDGE_HOOK_ENGAGED_JOINTS = [45.0, -10.0, -20.0, 0.0, 0.0, 30.0]
FRIDGE_PULL_JOINTS = [60.0, -10.0, -20.0, 0.0, 0.0, 30.0]
FRIDGE_RELEASE_JOINTS = [45.0, -20.0, -40.0, 0.0, 0.0, 0.0]
FRIDGE_GRAB_JOINTS = [45.0, -15.0, -30.0, 0.0, 0.0, 30.0]


@dataclass(frozen=True)
class PlateLayout:
    """Workspace-frame plate layout loaded from configs/plate_layout.yaml.

    Transforms plate-local coordinates to arm workspace frame.
    """

    origin_x_mm: float
    origin_y_mm: float
    origin_z_mm: float
    safe_z_mm: float
    approach_z_mm: float
    aspirate_z_mm: float
    dispense_z_mm: float
    trough_x_mm: float
    trough_y_mm: float
    trough_z_mm: float

    @classmethod
    def from_yaml(cls, path: str | Path) -> PlateLayout:
        """Load plate layout from YAML config.

        Args:
            path: Path to plate_layout.yaml.

        Returns:
            PlateLayout with workspace-frame coordinates.
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        plate = data["plate"]
        heights = data["heights"]
        trough = data.get("reagent_trough", {})

        return cls(
            origin_x_mm=plate["origin_x_mm"],
            origin_y_mm=plate["origin_y_mm"],
            origin_z_mm=plate["origin_z_mm"],
            safe_z_mm=heights["safe_z_mm"],
            approach_z_mm=heights["approach_z_mm"],
            aspirate_z_mm=heights["aspirate_z_mm"],
            dispense_z_mm=heights["dispense_z_mm"],
            trough_x_mm=trough.get("origin_x_mm", 200.0),
            trough_y_mm=trough.get("origin_y_mm", 0.0),
            trough_z_mm=trough.get("origin_z_mm", 25.0),
        )


def pipette_well(
    arm: DualArmController,
    pipette: PipetteProtocol,
    layout: PlateLayout,
    arm_id: str,
    source: str,
    dest: str,
    volume_ul: float,
) -> None:
    """Pipette from source to destination well.

    Core primitive: move arm to source, aspirate, move to dest, dispense.

    Args:
        arm: Arm controller (stub or real).
        pipette: Digital pipette (stub or real).
        layout: Plate layout with workspace coordinates.
        arm_id: Which arm to use.
        source: Source well name or "TROUGH".
        dest: Destination well name (e.g., "A1").
        volume_ul: Volume to transfer in microliters.

    Raises:
        ValueError: If dest is an invalid well name.
    """
    # Validate destination (raises ValueError if invalid)
    dest_well = parse_well_name(dest)

    # Move to source
    if source.upper() == "TROUGH":
        logger.info(
            "[UC1] Move %s → TROUGH (%.1f, %.1f mm)",
            arm_id,
            layout.trough_x_mm,
            layout.trough_y_mm,
        )
        arm.send_action(arm_id, [0.0] * 6)  # Stub: trough position
    else:
        arm.send_to_well(arm_id, source)

    # Aspirate
    logger.info("[UC1] Aspirate %.1f µL", volume_ul)
    pipette.aspirate(volume_ul)

    # Move to destination
    arm.send_to_well(arm_id, dest)

    # Dispense
    logger.info("[UC1] Dispense %.1f µL → %s", volume_ul, dest_well.name)
    pipette.dispense(volume_ul)


def uc1_single_well(
    arm: DualArmController,
    pipette: PipetteProtocol,
    layout: PlateLayout,
    arm_id: str,
    dest: str,
    volume_ul: float,
) -> None:
    """UC1.1: Pipette single well from trough.

    Args:
        arm: Arm controller.
        pipette: Digital pipette.
        layout: Plate layout.
        arm_id: Which arm to use.
        dest: Destination well name (e.g., "A1").
        volume_ul: Volume in microliters.
    """
    pipette_well(arm, pipette, layout, arm_id, "TROUGH", dest, volume_ul)


def uc1_row(
    arm: DualArmController,
    pipette: PipetteProtocol,
    layout: PlateLayout,
    arm_id: str,
    row: str,
    volume_ul: float,
) -> None:
    """UC1.2: Pipette entire row (12 wells) from trough.

    Args:
        arm: Arm controller.
        pipette: Digital pipette.
        layout: Plate layout.
        arm_id: Which arm to use.
        row: Row letter (A-H).
        volume_ul: Volume per well in microliters.

    Raises:
        ValueError: If row is not A-H.
    """
    row = row.upper()
    if row not in ROWS:
        raise ValueError(f"Invalid row: {row}. Must be A-H.")

    wells = [w for w in all_wells() if w.row == row]
    logger.info("[UC1] Pipetting row %s (%d wells, %.1f µL each)", row, len(wells), volume_ul)
    for well in wells:
        pipette_well(arm, pipette, layout, arm_id, "TROUGH", well.name, volume_ul)


def uc1_col(
    arm: DualArmController,
    pipette: PipetteProtocol,
    layout: PlateLayout,
    arm_id: str,
    col: int,
    volume_ul: float,
) -> None:
    """UC1.2: Pipette entire column (8 wells) from trough.

    Args:
        arm: Arm controller.
        pipette: Digital pipette.
        layout: Plate layout.
        arm_id: Which arm to use.
        col: Column number (1-12).
        volume_ul: Volume per well in microliters.

    Raises:
        ValueError: If col is not 1-12.
    """
    if col < 1 or col > 12:
        raise ValueError(f"Invalid column: {col}. Must be 1-12.")

    wells = [w for w in all_wells() if w.col == col]
    logger.info("[UC1] Pipetting column %d (%d wells, %.1f µL each)", col, len(wells), volume_ul)
    for well in wells:
        pipette_well(arm, pipette, layout, arm_id, "TROUGH", well.name, volume_ul)


def uc1_full_plate(
    arm: DualArmController,
    pipette: PipetteProtocol,
    layout: PlateLayout,
    arm_id: str,
    volume_ul: float,
) -> None:
    """UC1.3: Pipette all 96 wells from trough.

    Each well gets an individual aspirate/dispense cycle.

    Args:
        arm: Arm controller.
        pipette: Digital pipette.
        layout: Plate layout.
        arm_id: Which arm to use.
        volume_ul: Volume per well in microliters.
    """
    wells = all_wells()
    logger.info("[UC1] Pipetting full plate (%d wells, %.1f µL each)", len(wells), volume_ul)
    for well in wells:
        pipette_well(arm, pipette, layout, arm_id, "TROUGH", well.name, volume_ul)


def uc2_fridge_open_grab_move(
    arm: DualArmController,
    changer: ToolChanger,
    arm_id: str,
) -> None:
    """UC2: Open fridge with hook, swap to gripper, grab item, move out.

    Sequence:
    1. Equip fridge hook
    2. Approach fridge → hook door → pull open
    3. Swap to gripper
    4. Reach into fridge → grab item
    5. Park (move item to safe position)

    Args:
        arm: Arm controller.
        changer: Tool changer.
        arm_id: Which arm to use.
    """
    logger.info("[UC2] Starting fridge sequence")

    # Step 1: equip fridge hook
    changer.change_tool(Tool.FRIDGE_HOOK)

    # Step 2: open fridge door
    logger.info("[UC2] Approach fridge")
    arm.send_action(arm_id, FRIDGE_APPROACH_JOINTS)
    logger.info("[UC2] Engage hook — pull door")
    arm.send_action(arm_id, FRIDGE_HOOK_ENGAGED_JOINTS)
    arm.send_action(arm_id, FRIDGE_PULL_JOINTS)
    logger.info("[UC2] Release hook — door open")
    arm.send_action(arm_id, FRIDGE_RELEASE_JOINTS)

    # Step 3: swap to gripper
    changer.change_tool(Tool.GRIPPER)

    # Step 4: grab item
    logger.info("[UC2] Grab item from fridge")
    arm.send_action(arm_id, FRIDGE_GRAB_JOINTS)

    # Step 5: move to safe position
    arm.park_all()
    logger.info("[UC2] Fridge sequence complete — item at park position")


def uc3_tool_cycle(
    arm: DualArmController,
    changer: ToolChanger,
    arm_id: str,
    sequence: list[Tool] | None = None,
) -> None:
    """UC3: Cycle through tools to demonstrate interchange capability.

    Args:
        arm: Arm controller.
        changer: Tool changer.
        arm_id: Which arm to use.
        sequence: Tool sequence to follow. Default: PIPETTE → GRIPPER → FRIDGE_HOOK → GRIPPER.
    """
    if sequence is None:
        sequence = [Tool.PIPETTE, Tool.GRIPPER, Tool.FRIDGE_HOOK, Tool.GRIPPER]

    logger.info("[UC3] Starting tool cycle: %s", [t.value for t in sequence])
    for tool in sequence:
        changer.change_tool(tool)
        logger.info("[UC3] Equipped %s", tool.value)


def uc4_demo_all(
    arm: DualArmController,
    pipette: PipetteProtocol,
    changer: ToolChanger,
    layout: PlateLayout,
    arm_id: str = "arm_a",
) -> None:
    """UC4: Run all use cases in sequence (demo mode).

    Runs: UC1.1 → UC1.2 (row A) → UC1.2 (col 1) → UC2 → UC3 → park.
    Full plate is skipped in demo (too verbose); use uc1_full_plate directly.

    Args:
        arm: Arm controller.
        pipette: Digital pipette.
        changer: Tool changer.
        layout: Plate layout.
        arm_id: Which arm to use.
    """
    # Ensure pipette is equipped for UC1
    changer.change_tool(Tool.PIPETTE)

    logger.info("=== UC1.1: Single well (A1, 50 µL) ===")
    uc1_single_well(arm, pipette, layout, arm_id, "A1", 50.0)

    logger.info("=== UC1.2: Row A (25 µL each) ===")
    uc1_row(arm, pipette, layout, arm_id, "A", 25.0)

    logger.info("=== UC1.2: Column 1 (20 µL each) ===")
    uc1_col(arm, pipette, layout, arm_id, 1, 20.0)

    logger.info("=== UC2: Fridge open-grab-move ===")
    uc2_fridge_open_grab_move(arm, changer, arm_id)

    logger.info("=== UC3: Tool cycle ===")
    uc3_tool_cycle(arm, changer, arm_id)

    arm.park_all()
    logger.info("=== Demo complete ===")


def uc5_gantry_pipette(
    gantry: Any,
    pipette: PipetteProtocol,
    source: str,
    dest: str,
    volume_ul: float,
) -> None:
    """UC5: Pipette using XZ gantry (no SO-101 arm needed).

    Moves gantry to source, lowers, aspirates, raises, moves to dest, lowers,
    dispenses, raises. One aspirate-dispense cycle.

    Args:
        gantry: XZGantry controller (uses move_to_position, lower, raise_z).
        pipette: Any PipetteProtocol backend.
        source: Source position name in gantry config.
        dest: Destination position name in gantry config.
        volume_ul: Volume to transfer in microliters.
    """
    logger.info("[UC5] Gantry pipette: %s → %s (%.1f µL)", source, dest, volume_ul)

    gantry.move_to_position(source)
    gantry.lower()
    pipette.aspirate(volume_ul)
    gantry.raise_z()

    gantry.move_to_position(dest)
    gantry.lower()
    pipette.dispense(volume_ul)
    gantry.raise_z()

    logger.info("[UC5] Gantry pipette complete")


def uc5_gantry_strip(
    gantry: Any,
    pipette: PipetteProtocol,
    source: str,
    destinations: list[str],
    volume_ul: float,
) -> None:
    """UC5: Pipette a strip of positions using XZ gantry.

    Each destination gets an independent aspirate→dispense cycle from source.

    Args:
        gantry: XZGantry controller.
        pipette: Any PipetteProtocol backend.
        source: Source position name.
        destinations: List of destination position names.
        volume_ul: Volume per destination in microliters.
    """
    logger.info(
        "[UC5] Gantry strip: %s → %d destinations (%.1f µL each)",
        source, len(destinations), volume_ul,
    )
    for dest in destinations:
        uc5_gantry_pipette(gantry, pipette, source, dest, volume_ul)


def _create_pipette(pipette_config_path: str = "configs/pipette.yaml") -> PipetteProtocol:
    """Instantiate the correct pipette backend from config.

    Args:
        pipette_config_path: Path to pipette.yaml.

    Returns:
        A connected pipette satisfying PipetteProtocol.
    """
    try:
        with open(pipette_config_path) as f:
            data = yaml.safe_load(f)
        backend = data.get("backend", "digital_pipette_v2")
    except FileNotFoundError:
        backend = "digital_pipette_v2"
        data = {}

    if backend.startswith("electronic_"):
        section = data.get(backend, {})
        pipette: PipetteProtocol = ElectronicPipette(
            ElectronicPipetteConfig(
                serial_port=section.get("serial_port", "/dev/ttyACM0"),
                baud_rate=section.get("baud_rate", 9600),
                max_volume_ul=section.get("max_volume_ul", 1000.0),
                channels=section.get("channels", 1),
                model=section.get("model", "aelab_dpette_7016"),
            )
        )
    else:
        section = data.get("digital_pipette_v2", {})
        pipette = DigitalPipette(
            PipetteConfig(
                serial_port=section.get("serial_port", "/dev/ttyUSB0"),
                baud_rate=section.get("baud_rate", 9600),
                max_volume_ul=section.get("max_volume_ul", 200.0),
                actuator_stroke_mm=section.get("actuator_stroke_mm", 50.0),
            )
        )

    pipette.connect()
    return pipette


def create_workflow_context(
    arm_config_path: str = "configs/arms.yaml",
    dock_config_path: str = "configs/tool_dock.yaml",
    layout_path: str = "configs/plate_layout.yaml",
    pipette_config_path: str = "configs/pipette.yaml",
    arm_id: str = "arm_a",
) -> tuple[DualArmController, PipetteProtocol, ToolChanger, PlateLayout]:
    """Wire up all modules from config files.

    Returns connected controller, pipette, tool changer, and plate layout.
    All components work in stub mode when hardware is unavailable.

    Args:
        arm_config_path: Path to arms YAML config.
        dock_config_path: Path to tool dock YAML config.
        layout_path: Path to plate layout YAML config.
        pipette_config_path: Path to pipette backend YAML config.
        arm_id: Default arm ID for tool changer.

    Returns:
        Tuple of (arm_controller, pipette, tool_changer, plate_layout).
    """
    layout = PlateLayout.from_yaml(layout_path)
    arm_config = DualArmConfig.from_yaml(arm_config_path)
    arm = DualArmController(arm_config)
    arm.connect()

    pipette = _create_pipette(pipette_config_path)

    dock_config = ToolDockConfig.from_yaml(dock_config_path)
    changer = ToolChanger(dock_config, arm, arm_id)

    logger.info("Workflow context created (stub=%s)", arm._stub_mode)
    return arm, pipette, changer, layout
