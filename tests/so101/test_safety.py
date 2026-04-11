"""Tests for safety monitoring."""

import time

from hypothesis import given
from hypothesis import strategies as st

from so101.safety import JOINT_LIMITS, SafetyConfig, SafetyMonitor


class TestSafetyMonitor:
    """Test safety monitor behavior."""

    def test_e_stop_calls_park(self) -> None:
        parked = []
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: parked.append(True))
        monitor.e_stop()
        assert len(parked) == 1
        assert monitor.is_e_stopped

    def test_reset_e_stop(self) -> None:
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        monitor.e_stop()
        assert monitor.is_e_stopped
        monitor.reset_e_stop()
        assert not monitor.is_e_stopped

    def test_joint_limits_within(self) -> None:
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        assert monitor.check_joint_limits("shoulder_pan", 0.0) is True

    def test_joint_limits_exceeded(self) -> None:
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        assert monitor.check_joint_limits("shoulder_pan", 200.0) is False

    def test_joint_limits_unknown_joint(self) -> None:
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        assert monitor.check_joint_limits("unknown_joint", 999.0) is True

    def test_watchdog_triggers_park_on_timeout(self) -> None:
        parked = []
        config = SafetyConfig(watchdog_timeout_s=0.5)
        monitor = SafetyMonitor(config, park_callback=lambda: parked.append(True))
        monitor.start()
        time.sleep(1.5)
        monitor.stop()
        assert len(parked) >= 1

    def test_heartbeat_prevents_timeout(self) -> None:
        parked = []
        config = SafetyConfig(watchdog_timeout_s=1.0)
        monitor = SafetyMonitor(config, park_callback=lambda: parked.append(True))
        monitor.start()
        for _ in range(5):
            monitor.heartbeat()
            time.sleep(0.3)
        monitor.stop()
        assert len(parked) == 0

    def test_e_stop_is_idempotent(self) -> None:
        """Multiple e_stop calls park once each but stay stopped."""
        parked = []
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: parked.append(True))
        monitor.e_stop()
        monitor.e_stop()
        assert monitor.is_e_stopped
        assert len(parked) == 2

    def test_start_stop_idempotent(self) -> None:
        """Starting and stopping multiple times doesn't crash."""
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        monitor.start()
        monitor.stop()
        monitor.start()
        monitor.stop()

    def test_joint_limits_at_boundary(self) -> None:
        """Values exactly at limits are within bounds."""
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        assert monitor.check_joint_limits("shoulder_pan", -150.0) is True
        assert monitor.check_joint_limits("shoulder_pan", 150.0) is True

    def test_joint_limits_just_outside(self) -> None:
        """Values just outside limits are rejected."""
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        assert monitor.check_joint_limits("shoulder_pan", -150.1) is False
        assert monitor.check_joint_limits("shoulder_pan", 150.1) is False


class TestJointLimitProperties:
    """Hypothesis property tests for joint limits."""

    @given(
        joint=st.sampled_from(list(JOINT_LIMITS.keys())),
        data=st.data(),
    )
    def test_within_range_always_passes(self, joint: str, data: st.DataObject) -> None:
        """Any value within declared limits passes check."""
        lo, hi = JOINT_LIMITS[joint]
        value = data.draw(st.floats(min_value=lo, max_value=hi))
        monitor = SafetyMonitor(SafetyConfig(), park_callback=lambda: None)
        assert monitor.check_joint_limits(joint, value) is True
