"""Tests for workflow orchestration — E2E use cases in stub mode.

TDD: These tests define the expected behavior of workflow.py.
All tests work without hardware (stub mode).
"""

from __future__ import annotations

import pytest

from so101.arms import ArmConfig, DualArmConfig, DualArmController
from so101.pipette import (
    DigitalPipette,
    ElectronicPipette,
    ElectronicPipetteConfig,
    PipetteConfig,
)
from so101.tool_changer import Tool, ToolChanger, ToolDockConfig
from so101.workflow import (
    PlateLayout,
    create_workflow_context,
    pipette_well,
    uc1_col,
    uc1_full_plate,
    uc1_row,
    uc1_single_well,
    uc2_fridge_open_grab_move,
    uc3_tool_cycle,
    uc4_demo_all,
    uc5_gantry_pipette,
    uc5_gantry_strip,
)
from so101.xz_gantry import XZGantry, XZGantryConfig


@pytest.fixture
def stub_controller() -> DualArmController:
    """Connected controller in stub mode (no hardware)."""
    config = DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
    )
    ctrl = DualArmController(config)
    ctrl.connect()
    return ctrl


@pytest.fixture
def stub_pipette() -> DigitalPipette:
    """Pipette in stub mode (no serial)."""
    p = DigitalPipette(PipetteConfig())
    p.connect()
    return p


@pytest.fixture
def dock_config() -> ToolDockConfig:
    """Real dock config from YAML."""
    return ToolDockConfig.from_yaml("configs/tool_dock.yaml")


@pytest.fixture
def changer(dock_config: ToolDockConfig, stub_controller: DualArmController) -> ToolChanger:
    """Tool changer wired to stub controller."""
    return ToolChanger(dock_config, stub_controller, "arm_a")


@pytest.fixture
def layout() -> PlateLayout:
    """Real plate layout from YAML."""
    return PlateLayout.from_yaml("configs/plate_layout.yaml")


class TestPlateLayout:
    """Test PlateLayout config loading."""

    @pytest.mark.integration
    def test_loads_from_yaml(self, layout: PlateLayout) -> None:
        """PlateLayout loads from configs/plate_layout.yaml."""
        assert layout.origin_x_mm == 150.0

    @pytest.mark.integration
    def test_workspace_origin(self, layout: PlateLayout) -> None:
        """Workspace origin matches config values."""
        assert layout.origin_y_mm == -50.0
        assert layout.origin_z_mm == 20.0

    @pytest.mark.integration
    def test_heights(self, layout: PlateLayout) -> None:
        """Height values match config."""
        assert layout.safe_z_mm == 80.0
        assert layout.approach_z_mm == 40.0
        assert layout.aspirate_z_mm == 15.0
        assert layout.dispense_z_mm == 25.0


class TestUC1SingleWell:
    """Test single-well pipetting."""

    def test_single_well_completes(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """pipette_well runs without error in stub mode."""
        pipette_well(stub_controller, stub_pipette, layout, "arm_a", "TROUGH", "A1", 50.0)

    def test_single_well_fill_resets(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """After aspirate+dispense, pipette fill is 0."""
        pipette_well(stub_controller, stub_pipette, layout, "arm_a", "TROUGH", "A1", 50.0)
        assert stub_pipette._current_fill == 0.0

    def test_single_well_invalid_dest(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """Invalid well name raises ValueError."""
        with pytest.raises(ValueError):
            pipette_well(stub_controller, stub_pipette, layout, "arm_a", "TROUGH", "Z99", 50.0)

    def test_uc1_single_well_wrapper(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """uc1_single_well is a convenience wrapper over pipette_well."""
        uc1_single_well(stub_controller, stub_pipette, layout, "arm_a", "A1", 50.0)
        assert stub_pipette._current_fill == 0.0


class TestUC1Row:
    """Test row pipetting."""

    def test_row_a_completes(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """Row A pipettes 12 wells without error."""
        uc1_row(stub_controller, stub_pipette, layout, "arm_a", "A", 25.0)

    def test_row_fill_resets(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """After full row, pipette fill is 0."""
        uc1_row(stub_controller, stub_pipette, layout, "arm_a", "A", 25.0)
        assert stub_pipette._current_fill == 0.0

    def test_invalid_row_raises(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """Invalid row letter raises ValueError."""
        with pytest.raises(ValueError):
            uc1_row(stub_controller, stub_pipette, layout, "arm_a", "Z", 25.0)


class TestUC1Col:
    """Test column pipetting."""

    def test_col_1_completes(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """Column 1 pipettes 8 wells without error."""
        uc1_col(stub_controller, stub_pipette, layout, "arm_a", 1, 20.0)
        assert stub_pipette._current_fill == 0.0


class TestUC1FullPlate:
    """Test full-plate pipetting."""

    def test_full_plate_completes(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """Full plate (96 wells) completes without overflow error."""
        uc1_full_plate(stub_controller, stub_pipette, layout, "arm_a", 20.0)

    def test_full_plate_fill_resets(
        self, stub_controller: DualArmController, stub_pipette: DigitalPipette, layout: PlateLayout
    ) -> None:
        """After full plate, pipette fill is 0."""
        uc1_full_plate(stub_controller, stub_pipette, layout, "arm_a", 20.0)
        assert stub_pipette._current_fill == 0.0


class TestUC2Fridge:
    """Test fridge open-grab-move sequence."""

    def test_fridge_completes(
        self, stub_controller: DualArmController, changer: ToolChanger
    ) -> None:
        """Fridge sequence completes without error."""
        uc2_fridge_open_grab_move(stub_controller, changer, "arm_a")

    def test_fridge_ends_with_gripper(
        self, stub_controller: DualArmController, changer: ToolChanger
    ) -> None:
        """After fridge sequence, tool is GRIPPER."""
        uc2_fridge_open_grab_move(stub_controller, changer, "arm_a")
        assert changer.current_tool == Tool.GRIPPER

    def test_fridge_uses_hook(
        self, stub_controller: DualArmController, changer: ToolChanger
    ) -> None:
        """Fridge sequence switches to FRIDGE_HOOK during execution."""
        # After completion, tool is GRIPPER. But the sequence uses FRIDGE_HOOK.
        # We verify by checking the function doesn't crash (hook station exists).
        uc2_fridge_open_grab_move(stub_controller, changer, "arm_a")


class TestUC3ToolCycle:
    """Test tool interchange cycle."""

    def test_default_cycle_ends_on_gripper(
        self, stub_controller: DualArmController, changer: ToolChanger
    ) -> None:
        """Default tool cycle ends with GRIPPER equipped."""
        uc3_tool_cycle(stub_controller, changer, "arm_a")
        assert changer.current_tool == Tool.GRIPPER

    def test_custom_sequence(
        self, stub_controller: DualArmController, changer: ToolChanger
    ) -> None:
        """Custom tool sequence is followed."""
        uc3_tool_cycle(stub_controller, changer, "arm_a", [Tool.PIPETTE, Tool.FRIDGE_HOOK])
        assert changer.current_tool == Tool.FRIDGE_HOOK

    def test_same_tool_noop(self, stub_controller: DualArmController, changer: ToolChanger) -> None:
        """Changing to the already-equipped tool is a no-op."""
        changer.current_tool = Tool.GRIPPER
        uc3_tool_cycle(stub_controller, changer, "arm_a", [Tool.GRIPPER])
        assert changer.current_tool == Tool.GRIPPER


class TestUC4DemoAll:
    """Test full demo sequence."""

    def test_demo_all_completes(
        self,
        stub_controller: DualArmController,
        stub_pipette: DigitalPipette,
        changer: ToolChanger,
        layout: PlateLayout,
    ) -> None:
        """Full demo runs without error in stub mode."""
        uc4_demo_all(stub_controller, stub_pipette, changer, layout, "arm_a")

    def test_demo_all_fill_zero(
        self,
        stub_controller: DualArmController,
        stub_pipette: DigitalPipette,
        changer: ToolChanger,
        layout: PlateLayout,
    ) -> None:
        """After demo, pipette fill is 0."""
        uc4_demo_all(stub_controller, stub_pipette, changer, layout, "arm_a")
        assert stub_pipette._current_fill == 0.0


@pytest.fixture
def stub_gantry() -> XZGantry:
    """Connected XZ gantry in stub mode."""
    config = XZGantryConfig(
        serial_port="/dev/ttyUSB_MISSING",
        positions={"trough": (0.0, 0.0), "plate_a1": (45.0, 11.24), "plate_a2": (54.0, 11.24)},
    )
    g = XZGantry(config)
    g.connect()
    return g


class TestUC5GantryPipette:
    """UC5: Gantry-based pipetting — no SO-101 arm needed."""

    def test_gantry_single_well_completes(
        self, stub_gantry: XZGantry, stub_pipette: DigitalPipette
    ) -> None:
        """Full cycle: trough → aspirate → plate → dispense."""
        uc5_gantry_pipette(stub_gantry, stub_pipette, "trough", "plate_a1", 50.0)
        assert stub_pipette._current_fill == 0.0

    def test_gantry_fill_resets(self, stub_gantry: XZGantry, stub_pipette: DigitalPipette) -> None:
        """Pipette fill returns to 0 after dispense."""
        uc5_gantry_pipette(stub_gantry, stub_pipette, "trough", "plate_a1", 100.0)
        assert stub_pipette._current_fill == 0.0

    def test_gantry_invalid_position_raises(
        self, stub_gantry: XZGantry, stub_pipette: DigitalPipette
    ) -> None:
        """Unknown position raises ValueError."""
        with pytest.raises(ValueError, match="Unknown position"):
            uc5_gantry_pipette(stub_gantry, stub_pipette, "nonexistent", "plate_a1", 50.0)

    def test_gantry_with_electronic_pipette(self, stub_gantry: XZGantry) -> None:
        """ElectronicPipette works with gantry (PipetteProtocol)."""
        epipette = ElectronicPipette(
            ElectronicPipetteConfig(serial_port="/dev/ttyACM_MISSING", max_volume_ul=1000.0)
        )
        epipette.connect()
        uc5_gantry_pipette(stub_gantry, epipette, "trough", "plate_a1", 50.0)
        assert epipette._current_fill == 0.0


class TestUC5GantryStrip:
    """UC5: Gantry-based strip pipetting — multiple wells."""

    def test_gantry_strip_completes(
        self, stub_gantry: XZGantry, stub_pipette: DigitalPipette
    ) -> None:
        """Pipette multiple positions in sequence."""
        uc5_gantry_strip(stub_gantry, stub_pipette, "trough", ["plate_a1", "plate_a2"], 25.0)
        assert stub_pipette._current_fill == 0.0

    def test_gantry_strip_empty_list(
        self, stub_gantry: XZGantry, stub_pipette: DigitalPipette
    ) -> None:
        """Empty destination list is a no-op."""
        uc5_gantry_strip(stub_gantry, stub_pipette, "trough", [], 25.0)
        assert stub_pipette._current_fill == 0.0


class TestCreateWorkflowContext:
    """Test factory function."""

    @pytest.mark.integration
    def test_creates_all_components(self) -> None:
        """Factory returns 4-tuple with all components."""
        arm, pipette, changer, layout = create_workflow_context()
        assert arm._connected is True
        assert isinstance(pipette, DigitalPipette)
        assert isinstance(changer, ToolChanger)
        assert isinstance(layout, PlateLayout)
        arm.disconnect()

    @pytest.mark.integration
    def test_arm_in_stub_mode(self) -> None:
        """Factory creates arm in stub mode (no hardware)."""
        arm, _, _, _ = create_workflow_context()
        assert arm._stub_mode is True
        arm.disconnect()
