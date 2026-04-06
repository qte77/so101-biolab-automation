"""Tests for XZGantry dedicated pipetting arm controller."""

import pytest

from biolab.xz_gantry import XZGantry, XZGantryConfig


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
