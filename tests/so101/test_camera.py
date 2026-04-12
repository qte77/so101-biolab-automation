"""Tests for camera pipeline — must work without cv2/camera hardware."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import numpy as np
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


def _make_mock_cv2() -> MagicMock:
    """Create a mock cv2 module with required constants."""
    mock_cv2 = MagicMock()
    mock_cv2.CAP_PROP_FRAME_WIDTH = 3
    mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
    mock_cv2.CAP_PROP_FPS = 5
    return mock_cv2


class TestCameraPipelineWithMockCV2:
    """Tests covering cv2-dependent paths with mocked VideoCapture."""

    def test_start_opens_cameras(self) -> None:
        """start() calls VideoCapture and sets properties for each camera."""
        mock_cv2 = _make_mock_cv2()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cv2.VideoCapture.return_value = mock_cap

        with patch.dict(sys.modules, {"cv2": mock_cv2}):
            pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
            pipeline.start()
            mock_cv2.VideoCapture.assert_called_once_with(0)
            assert "test" in pipeline._captures

    def test_start_skips_failed_camera(self) -> None:
        """start() skips cameras that fail to open."""
        mock_cv2 = _make_mock_cv2()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cv2.VideoCapture.return_value = mock_cap

        with patch.dict(sys.modules, {"cv2": mock_cv2}):
            pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
            pipeline.start()
            assert pipeline._captures == {}

    def test_stop_releases_captures(self) -> None:
        """stop() calls release() on all open captures."""
        mock_cv2 = _make_mock_cv2()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cv2.VideoCapture.return_value = mock_cap

        with patch.dict(sys.modules, {"cv2": mock_cv2}):
            pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
            pipeline.start()
            pipeline.stop()
            mock_cap.release.assert_called_once()
            assert pipeline._captures == {}

    def test_get_frame_returns_array(self) -> None:
        """get_frame() returns the frame when capture succeeds."""
        mock_cv2 = _make_mock_cv2()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2.VideoCapture.return_value = mock_cap

        with patch.dict(sys.modules, {"cv2": mock_cv2}):
            pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
            pipeline.start()
            frame = pipeline.get_frame("test")
            assert frame is not None
            assert frame.shape == (480, 640, 3)

    def test_get_frame_returns_none_on_read_failure(self) -> None:
        """get_frame() returns None when cap.read() fails."""
        mock_cv2 = _make_mock_cv2()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_cv2.VideoCapture.return_value = mock_cap

        with patch.dict(sys.modules, {"cv2": mock_cv2}):
            pipeline = CameraPipeline([CameraConfig(name="test", device_index=0)])
            pipeline.start()
            assert pipeline.get_frame("test") is None

    def test_get_frames_aggregates_multiple(self) -> None:
        """get_frames() returns dict of all active camera frames."""
        fake = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cv2 = _make_mock_cv2()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, fake)
        mock_cv2.VideoCapture.return_value = mock_cap

        with patch.dict(sys.modules, {"cv2": mock_cv2}):
            configs = [
                CameraConfig(name="a", device_index=0),
                CameraConfig(name="b", device_index=2),
            ]
            pipeline = CameraPipeline(configs)
            pipeline.start()
            frames = pipeline.get_frames()
            assert "a" in frames
            assert "b" in frames
