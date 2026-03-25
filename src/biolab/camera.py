"""Multi-camera pipeline for workspace monitoring.

Captures from overhead + wrist cameras, provides frames for:
- WebRTC streaming to remote dashboard
- LeRobot dataset recording
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    """Configuration for a single camera."""

    name: str
    device_index: int  # /dev/videoN or index
    width: int = 640
    height: int = 480
    fps: int = 30


class CameraPipeline:
    """Manages multiple cameras for the biolab workspace.

    Usage:
        pipeline = CameraPipeline([
            CameraConfig("overhead", 0),
            CameraConfig("wrist_a", 2),
            CameraConfig("wrist_b", 4),
        ])
        pipeline.start()
        frames = pipeline.get_frames()  # {"overhead": ndarray, ...}
        pipeline.stop()
    """

    def __init__(self, cameras: list[CameraConfig]) -> None:
        self.cameras = {cam.name: cam for cam in cameras}
        self._captures: dict[str, Any] = {}

    def start(self) -> None:
        """Open all camera devices. Requires cv2 (opencv-python)."""
        try:
            import cv2
        except ImportError:
            logger.warning("cv2 not available — cameras disabled")
            return

        for name, cfg in self.cameras.items():
            cap = cv2.VideoCapture(cfg.device_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
            cap.set(cv2.CAP_PROP_FPS, cfg.fps)

            if not cap.isOpened():
                logger.warning("Failed to open camera %s (device %d)", name, cfg.device_index)
                continue

            self._captures[name] = cap
            logger.info(
                "Camera %s opened (device %d, %dx%d@%dfps)",
                name, cfg.device_index, cfg.width, cfg.height, cfg.fps,
            )

    def stop(self) -> None:
        """Release all camera devices."""
        for name, cap in self._captures.items():
            cap.release()
            logger.info("Camera %s released", name)
        self._captures.clear()

    def get_frame(self, name: str) -> Any | None:
        """Capture a single frame from a named camera.

        Args:
            name: Camera name.

        Returns:
            BGR image as numpy array, or None if capture failed.
        """
        cap = self._captures.get(name)
        if cap is None:
            return None
        ret, frame = cap.read()
        return frame if ret else None

    def get_frames(self) -> dict[str, Any]:
        """Capture frames from all active cameras.

        Returns:
            Dict mapping camera name to BGR image array.
        """
        frames = {}
        for name in self._captures:
            frame = self.get_frame(name)
            if frame is not None:
                frames[name] = frame
        return frames
