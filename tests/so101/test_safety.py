"""Tests for safety monitoring."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from so101 import safety
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

    def test_watchdog_triggers_park_on_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Watchdog parks arms once the heartbeat goes past the timeout.

        Drives virtual time via a patched ``time.monotonic`` so the test is
        deterministic — no real sleeping, no background-thread race.
        """
        fake_time = [1000.0]
        monkeypatch.setattr(safety.time, "monotonic", lambda: fake_time[0])

        parked: list[bool] = []
        config = SafetyConfig(watchdog_timeout_s=0.5)
        monitor = SafetyMonitor(config, park_callback=lambda: parked.append(True))

        fake_time[0] += 1.5  # 1.5s > 0.5s timeout
        monitor._check_watchdog()

        assert parked == [True]
        assert monitor.is_e_stopped

    def test_heartbeat_prevents_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Regular heartbeats keep the watchdog from ever firing."""
        fake_time = [1000.0]
        monkeypatch.setattr(safety.time, "monotonic", lambda: fake_time[0])

        parked: list[bool] = []
        config = SafetyConfig(watchdog_timeout_s=1.0)
        monitor = SafetyMonitor(config, park_callback=lambda: parked.append(True))

        for _ in range(5):
            fake_time[0] += 0.3  # advance below timeout
            monitor.heartbeat()
            monitor._check_watchdog()

        assert parked == []
        assert not monitor.is_e_stopped

    def test_watchdog_latches_e_stop_after_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """After a timeout-triggered park, further checks are a no-op.

        Latching ensures the operator has to explicitly reset the e-stop
        after a watchdog-driven park — a subsequent tick must not call
        park() a second time or clear the e_stop flag on its own.
        """
        fake_time = [1000.0]
        monkeypatch.setattr(safety.time, "monotonic", lambda: fake_time[0])

        parked: list[bool] = []
        config = SafetyConfig(watchdog_timeout_s=0.5)
        monitor = SafetyMonitor(config, park_callback=lambda: parked.append(True))

        fake_time[0] += 1.0  # past timeout
        monitor._check_watchdog()
        fake_time[0] += 5.0  # way past
        monitor._check_watchdog()
        monitor._check_watchdog()

        assert parked == [True]  # park called exactly once
        assert monitor.is_e_stopped

        # Explicit reset clears the latch
        monitor.reset_e_stop()
        assert not monitor.is_e_stopped

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
