"""Tests for camera pipeline — must work without cv2/camera hardware."""

import pytest
from pydantic import ValidationError

from so101.camera import CameraConfig, CameraPipeline


class TestCameraConfigModel:
    """CameraConfig pydantic model validation."""

    def test_construction_keyword(self) -> None:
        cfg = CameraConfig(name="overhead", device_index=0)
        assert cfg.name == "overhead"
        assert cfg.device_index == 0

    def test_strict_rejects_str_for_int(self) -> None:
        with pytest.raises(ValidationError):
            CameraConfig(name="test", device_index="0")  # type: ignore[arg-type]

    def test_defaults(self) -> None:
        cfg = CameraConfig(name="test", device_index=0)
        assert cfg.width == 640
        assert cfg.height == 480
        assert cfg.fps == 30


class TestCameraPipeline:
    """Test CameraPipeline in headless environment (no cv2, no cameras)."""

    def test_import_without_cv2(self) -> None:
        """CameraPipeline can be imported even if cv2 is unavailable."""
        pipeline = CameraPipeline([])
        assert pipeline is not None

    def test_instantiate_with_configs(self) -> None:
        """CameraPipeline stores camera configs by name."""
        configs = [
            CameraConfig(name="overhead", device_index=0),
            CameraConfig(name="wrist", device_index=2),
        ]
        pipeline = CameraPipeline(configs)
        assert "overhead" in pipeline.cameras
        assert "wrist" in pipeline.cameras

    @pytest.mark.hardware
    def test_start_without_cv2(self) -> None:
        """start() gracefully handles missing cv2.

        Marked ``hardware`` because when cv2 IS installed in the dev env,
        ``start()`` calls ``cv2.VideoCapture(0)`` which opens a real camera
        device if /dev/video0 exists. Excluded from the default suite to
        keep CI portable; run with ``pytest -m hardware`` on a rig.
        """
        pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
        # cv2 may or may not be installed — either way, start should not crash
        pipeline.start()
        pipeline.stop()

    def test_get_frame_closed_camera(self) -> None:
        """get_frame returns None for a camera that was never opened."""
        pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
        assert pipeline.get_frame("test") is None

    def test_get_frame_unknown_camera(self) -> None:
        """get_frame returns None for an unknown camera name."""
        pipeline = CameraPipeline([])
        assert pipeline.get_frame("nonexistent") is None

    def test_get_frames_empty(self) -> None:
        """get_frames returns empty dict when no cameras are open."""
        pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
        assert pipeline.get_frames() == {}

    def test_stop_idempotent(self) -> None:
        """stop() can be called multiple times without error."""
        pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
        pipeline.stop()
        pipeline.stop()
