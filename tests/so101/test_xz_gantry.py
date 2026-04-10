"""Tests for XZGantry dedicated pipetting arm controller."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from so101.xz_gantry import XZGantry, XZGantryConfig


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
        gantry.move_to_position("trough")
        assert gantry._current_x == pytest.approx(0.0)

    def test_move_to_unknown_position_raises(self, gantry: XZGantry) -> None:
        with pytest.raises(ValueError, match="Unknown position"):
            gantry.move_to_position("nonexistent")

    def test_lower_raise_cycle(self, gantry: XZGantry) -> None:
        gantry.move_to_position("plate_a1")
        gantry.lower()
        assert gantry._current_z == pytest.approx(gantry.config.approach_z_mm)
        gantry.raise_z()
        assert gantry._current_z == pytest.approx(gantry.config.safe_z_mm)


class TestXZGantryProtocols:
    """Tests for controller-specific serial protocols."""

    def test_maestro_command_format(self) -> None:
        """Pololu Maestro uses compact binary protocol (0x84)."""
        g = XZGantry(XZGantryConfig(controller="pololu_maestro"))
        g._serial = MagicMock()
        g._stub_mode = False
        g._send_command("MOVE_X 100.0")
        g._serial.write.assert_called_once()
        data = g._serial.write.call_args[0][0]
        assert isinstance(data, bytes)
        assert data[0] == 0x84  # Maestro compact protocol command byte

    def test_pico_command_format(self) -> None:
        """Pico W uses plain text protocol."""
        g = XZGantry(XZGantryConfig(controller="pico_w"))
        g._serial = MagicMock()
        g._stub_mode = False
        g._send_command("MOVE_X 100.0")
        g._serial.write.assert_called_once()
        data = g._serial.write.call_args[0][0]
        assert data == b"MOVE_X 100.0\n"


class TestXZGantryTeaching:
    """Tests for position teaching and config persistence."""

    def test_teach_position(self, gantry: XZGantry) -> None:
        """teach_position saves current X/Z as a named position."""
        gantry._current_x = 77.5
        gantry._current_z = 30.0
        gantry.teach_position("new_spot")
        assert "new_spot" in gantry.config.positions
        assert gantry.config.positions["new_spot"] == pytest.approx((77.5, 30.0))

    def test_save_config(self, gantry: XZGantry, tmp_path: object) -> None:
        """save_config writes positions to YAML."""
        import yaml

        out = tmp_path / "gantry_out.yaml"  # type: ignore[operator]
        gantry.teach_position("taught")
        gantry.save_config(str(out))
        data = yaml.safe_load(out.read_text())  # type: ignore[union-attr]
        assert "taught" in data["positions"]
