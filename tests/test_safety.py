"""Tests for safety monitoring."""

import time

import pytest

from biolab.safety import SafetyConfig, SafetyMonitor


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
