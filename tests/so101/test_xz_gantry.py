"""Tests for XZGantry dedicated pipetting arm controller."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from so101.xz_gantry import XZGantry, XZGantryConfig


class TestXZGantryConfigModel:
    """Strict pydantic-settings validation for XZGantryConfig."""

    def test_defaults(self) -> None:
        """Default construction uses field defaults (no auto-YAML)."""
        cfg = XZGantryConfig()
        assert cfg.serial_port == "/dev/ttyUSB1"
        assert cfg.positions == {}

    def test_strict_rejects_str_for_int(self) -> None:
        with pytest.raises(ValidationError):
            XZGantryConfig(baud_rate="115200")  # type: ignore[arg-type]

    def test_positions_tuples(self) -> None:
        cfg = XZGantryConfig(positions={"a": (1.0, 2.0)})
        assert cfg.positions["a"] == (1.0, 2.0)

    def test_positions_lists_coerced_to_tuples(self) -> None:
        """YAML loads positions as lists — before-validator coerces to tuples."""
        cfg = XZGantryConfig.model_validate({"positions": {"a": [1.0, 2.0]}})
        assert cfg.positions["a"] == (1.0, 2.0)

    @pytest.mark.integration
    def test_from_yaml(self) -> None:
        cfg = XZGantryConfig.from_yaml("configs/xz_gantry.yaml")
        assert cfg.serial_port == "/dev/ttyUSB1"
        assert "trough" in cfg.positions
        assert isinstance(cfg.positions["trough"], tuple)


@pytest.fixture
def gantry() -> XZGantry:
    """Return an XZ gantry in stub mode."""
    config = XZGantryConfig(
        serial_port="/dev/ttyUSB_MISSING",
        positions={"trough": (0.0, 0.0), "plate_a1": (45.0, 11.24), "waste": (120.0, 0.0)},
    )
    g = XZGantry(config)
    g.connect()
    return g


class TestXZGantryConnect:
    """Tests for connection and stub mode."""

    def test_connect_stub_mode(self) -> None:
        g = XZGantry(XZGantryConfig(serial_port="/dev/ttyUSB_MISSING"))
        g.connect()  # should not raise

    def test_disconnect(self, gantry: XZGantry) -> None:
        gantry.disconnect()


class TestXZGantryMotion:
    """Tests for position movement."""

    def test_move_to_known_position(self, gantry: XZGantry) -> None:
        """Moving to a configured position does not raise."""
        gantry.move_to_position("trough")

    def test_move_to_unknown_position_raises(self, gantry: XZGantry) -> None:
        with pytest.raises(ValueError, match="Unknown position"):
            gantry.move_to_position("nonexistent")

    def test_move_twice_to_same_position(self, gantry: XZGantry) -> None:
        """Moving to the same position twice is idempotent."""
        gantry.move_to_position("plate_a1")
        gantry.move_to_position("plate_a1")

    def test_lower_raise_cycle(self, gantry: XZGantry) -> None:
        """Lower then raise completes without error."""
        gantry.move_to_position("plate_a1")
        gantry.lower()
        gantry.raise_z()


class TestXZGantryProtocols:
    """Tests for controller-specific serial wire format.

    These drive the pure ``encode_maestro`` / ``encode_pico`` static methods —
    no serial, no mocks, no hardware. The encoders are what must match what
    real controllers expect, so pinning their byte-level output is the
    behavioural contract to test.
    """

    def test_maestro_command_format(self) -> None:
        """Pololu Maestro uses compact binary protocol starting with 0x84."""
        data = XZGantry.encode_maestro("MOVE_X 100.0", x_range_mm=200.0, z_range_mm=100.0)
        assert isinstance(data, bytes)
        assert len(data) == 4  # 0x84 + channel + 2-byte target
        assert data[0] == 0x84  # Maestro compact protocol command byte
        assert data[1] == 0  # X axis → channel 0

    def test_maestro_z_uses_channel_1(self) -> None:
        """Z-axis commands map to Maestro servo channel 1."""
        data = XZGantry.encode_maestro("MOVE_Z 50.0", x_range_mm=200.0, z_range_mm=100.0)
        assert data[1] == 1  # Z axis → channel 1

    def test_maestro_target_scales_with_range(self) -> None:
        """Half-range input maps to the mid-point of the 4000-8000 servo range."""
        import struct

        data = XZGantry.encode_maestro("MOVE_X 100.0", x_range_mm=200.0, z_range_mm=100.0)
        _, _, target = struct.unpack("<BBH", data)
        assert target == 6000  # 4000 + 0.5 * 4000

    def test_pico_command_format(self) -> None:
        """Pico W uses newline-terminated plain text."""
        data = XZGantry.encode_pico("MOVE_X 100.0")
        assert data == b"MOVE_X 100.0\n"


class TestXZGantryTeaching:
    """Tests for position teaching and config persistence."""

    def test_teach_then_move(self, gantry: XZGantry) -> None:
        """After teaching a position, moving to it succeeds."""
        gantry.move_to_position("trough")
        gantry.teach_position("new_spot")
        gantry.move_to_position("plate_a1")
        gantry.move_to_position("new_spot")  # should not raise

    def test_save_config(self, gantry: XZGantry, tmp_path: object) -> None:
        """save_config writes positions to YAML."""
        import yaml

        out = tmp_path / "gantry_out.yaml"  # type: ignore[operator]
        gantry.teach_position("taught")
        gantry.save_config(str(out))
        data = yaml.safe_load(out.read_text())  # type: ignore[union-attr]
        assert "taught" in data["positions"]
