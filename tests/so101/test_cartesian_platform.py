"""Tests for Cartesian motion platform (Voron/Moonraker)."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from so101.cartesian_platform import CartesianConfig, CartesianPlatform


class TestCartesianConfigModel:
    """Strict pydantic-settings validation for CartesianConfig."""

    def test_defaults(self) -> None:
        """Default construction uses field defaults."""
        cfg = CartesianConfig()
        assert cfg.moonraker_url == "http://localhost:7125"
        assert cfg.timeout_s == 10.0
        assert cfg.safe_z_mm == 50.0
        assert cfg.feedrate == 3000
        assert cfg.approach_z_mm == 5.0
        assert cfg.positions == {}

    def test_strict_rejects_str_for_int(self) -> None:
        """Feedrate must be int, not str."""
        with pytest.raises(ValidationError):
            CartesianConfig(feedrate="3000")  # type: ignore[arg-type]

    def test_strict_rejects_str_for_float(self) -> None:
        """safe_z_mm must be float, not str."""
        with pytest.raises(ValidationError):
            CartesianConfig(safe_z_mm="50")  # type: ignore[arg-type]

    def test_positions_coerce_lists_to_tuples(self) -> None:
        """YAML loads positions as lists -- before-validator coerces to tuples."""
        cfg = CartesianConfig.model_validate({"positions": {"home": [0.0, 0.0, 0.0]}})
        assert cfg.positions["home"] == (0.0, 0.0, 0.0)
        assert isinstance(cfg.positions["home"], tuple)

    @pytest.mark.integration
    def test_from_yaml(self) -> None:
        """Load config from the shipped YAML file."""
        cfg = CartesianConfig.from_yaml("configs/cartesian.yaml")
        assert cfg.moonraker_url == "http://localhost:7125"
        assert "home" in cfg.positions
        assert isinstance(cfg.positions["home"], tuple)
        assert len(cfg.positions["home"]) == 3


class TestEncodeMove:
    """Pure function tests for G-code move encoding -- no mocks."""

    def test_encode_basic(self) -> None:
        """Standard coordinate encoding."""
        result = CartesianPlatform.encode_move(10, 20, 5, 3000)
        assert result == "G0 X10.000 Y20.000 Z5.000 F3000"

    def test_encode_negative(self) -> None:
        """Negative coordinates are valid G-code."""
        result = CartesianPlatform.encode_move(-10, -20, -5, 1500)
        assert result == "G0 X-10.000 Y-20.000 Z-5.000 F1500"

    def test_encode_zero(self) -> None:
        """All-zero coordinates."""
        result = CartesianPlatform.encode_move(0, 0, 0, 3000)
        assert result == "G0 X0.000 Y0.000 Z0.000 F3000"


@pytest.fixture
def platform() -> CartesianPlatform:
    """Return a CartesianPlatform in stub mode (no Moonraker)."""
    config = CartesianConfig(
        moonraker_url="http://127.0.0.1:1",  # unreachable
        positions={
            "home": (0.0, 0.0, 0.0),
            "plate_a1": (150.0, -50.0, 20.0),
            "reagent_trough": (100.0, -80.0, 30.0),
        },
    )
    p = CartesianPlatform(config)
    p.connect()
    return p


class TestCartesianPlatformStubMode:
    """Tests for connection fallback to stub mode."""

    def test_connect_unreachable_enters_stub(self) -> None:
        """Connecting to an unreachable URL enters stub mode."""
        cfg = CartesianConfig(moonraker_url="http://127.0.0.1:1")
        p = CartesianPlatform(cfg)
        p.connect()
        assert p.is_stub_mode is True

    def test_is_stub_mode_property(self, platform: CartesianPlatform) -> None:
        """is_stub_mode property reflects stub state."""
        assert platform.is_stub_mode is True

    def test_disconnect_idempotent(self, platform: CartesianPlatform) -> None:
        """Calling disconnect multiple times does not raise."""
        platform.disconnect()
        platform.disconnect()


class TestCartesianPlatformMotion:
    """Motion tests using stub mode."""

    def test_home_sends_g28(self, platform: CartesianPlatform) -> None:
        """home() sends G28 via gcode log."""
        platform.home()
        assert "G28" in platform._gcode_log

    def test_move_to_updates_position(self, platform: CartesianPlatform) -> None:
        """move_to updates the tracked position."""
        platform.move_to(10.0, 20.0, 5.0)
        assert platform.get_position() == (10.0, 20.0, 5.0)

    def test_move_to_position_named(self, platform: CartesianPlatform) -> None:
        """move_to_position delegates to move_to with configured coords."""
        platform.move_to_position("plate_a1")
        assert platform.get_position() == (150.0, -50.0, 20.0)

    def test_move_to_position_unknown_raises(self, platform: CartesianPlatform) -> None:
        """Unknown position name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown position"):
            platform.move_to_position("nonexistent")

    def test_raise_to_safe(self, platform: CartesianPlatform) -> None:
        """raise_to_safe sets Z to safe_z_mm, preserving X and Y."""
        platform.move_to(10.0, 20.0, 5.0)
        platform.raise_to_safe()
        pos = platform.get_position()
        assert pos[0] == 10.0
        assert pos[1] == 20.0
        assert pos[2] == platform.config.safe_z_mm

    def test_gcode_log_records_commands(self, platform: CartesianPlatform) -> None:
        """Stub mode logs all G-code commands sent."""
        platform.home()
        platform.move_to(1.0, 2.0, 3.0)
        platform.raise_to_safe()
        assert len(platform._gcode_log) == 3
        assert platform._gcode_log[0] == "G28"
        assert platform._gcode_log[1].startswith("G0 ")


class TestCartesianPlatformHypothesis:
    """Property-based tests for encode_move."""

    @given(
        x=st.floats(min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False),
        z=st.floats(min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False),
    )
    def test_encode_move_format(self, x: float, y: float, z: float) -> None:
        """encode_move always produces a G0 command with X, Y, Z, F fields."""
        result = CartesianPlatform.encode_move(x, y, z, 3000)
        assert result.startswith("G0 ")
        assert " X" in result
        assert " Y" in result
        assert " Z" in result
        assert " F3000" in result

    @given(feedrate=st.integers(min_value=1, max_value=10000))
    def test_encode_move_feedrate(self, feedrate: int) -> None:
        """encode_move embeds the feedrate as an integer."""
        result = CartesianPlatform.encode_move(0, 0, 0, feedrate)
        assert f"F{feedrate}" in result
