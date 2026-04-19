r"""Live SO-101 arm visualization via Foxglove WebSocket + optional MCAP.

Reads joint positions from a real SO-101 follower arm, computes forward
kinematics via URDF, and streams transforms + camera frames to Foxglove.

Requires dependency groups: ``uv sync --group foxglove --group lerobot``

URDF and STL assets are maintained upstream:
https://github.com/foxglove/foxglove-sdk/tree/main/python/foxglove-sdk-examples/so101-visualization/SO101

Usage::

    python -m so101.foxglove_viz \
        --robot.port=/dev/ttyACM1 --robot.id=arm_a \
        --robot.wrist_cam_id=2 --robot.env_cam_id=0
"""

from __future__ import annotations

import argparse
import datetime
import logging
import math
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

RATE_HZ = 30.0
WORLD_FRAME_ID = "world"
BASE_FRAME_ID = "base_link"
URDF_FILE = "SO101/so101_new_calib.urdf"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SO-101 live visualization via Foxglove",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    robot = parser.add_argument_group("robot")
    robot.add_argument("--robot.port", required=True, dest="port")
    robot.add_argument("--robot.id", required=True, dest="robot_id")
    robot.add_argument("--robot.wrist_cam_id", type=int, dest="wrist_cam_id")
    robot.add_argument("--robot.env_cam_id", type=int, dest="env_cam_id")

    out = parser.add_argument_group("output")
    out.add_argument("--output.write_mcap", action="store_true", dest="write_mcap")
    out.add_argument("--output.mcap_path", dest="mcap_path")
    out.add_argument("--urdf", default=URDF_FILE, help="Path to SO-101 URDF file")
    return parser.parse_args()


def _setup_camera(cam_id: int, topic: str) -> tuple[Any, Any]:
    """Connect camera and create Foxglove image channel."""
    from foxglove.channels import RawImageChannel
    from lerobot.cameras import ColorMode, Cv2Rotation
    from lerobot.cameras.opencv import OpenCVCamera, OpenCVCameraConfig

    cfg = OpenCVCameraConfig(
        index_or_path=cam_id,
        fps=30,
        width=640,
        height=480,
        color_mode=ColorMode.RGB,
        rotation=Cv2Rotation.NO_ROTATION,
    )
    camera = OpenCVCamera(cfg)
    camera.connect()
    channel = RawImageChannel(topic=topic)
    return camera, channel


def _publish_frame(camera: Any, channel: Any) -> None:
    """Read one frame and publish to Foxglove."""
    from foxglove.messages import RawImage

    frame = camera.async_read(timeout_ms=200)
    channel.log(
        RawImage(
            data=frame.tobytes(),
            width=frame.shape[1],
            height=frame.shape[0],
            step=frame.shape[1] * 3,
            encoding="rgb8",
        ),
    )


_JOINT_KEYS = [
    "shoulder_pan", "shoulder_lift", "elbow_flex",
    "wrist_flex", "wrist_roll",
]


def _read_joints(obs: Any, positions: dict[str, float]) -> None:
    """Update joint positions from follower observation (degrees → radians)."""
    for key in _JOINT_KEYS:
        positions[key] = math.radians(obs.get(f"{key}.pos", 0.0))
    positions["gripper"] = (obs.get("gripper.pos", 0.0) - 10) / 100.0 * math.pi


def _build_transforms(robot_model: Any) -> list[Any]:
    """Compute per-joint transforms from URDF forward kinematics."""
    from foxglove.messages import FrameTransform, Quaternion, Vector3
    from scipy.spatial.transform import Rotation

    transforms: list[Any] = [
        FrameTransform(
            parent_frame_id=WORLD_FRAME_ID,
            child_frame_id=BASE_FRAME_ID,
            translation=Vector3(x=0.0, y=0.0, z=0.0),
            rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        ),
    ]
    for joint in robot_model.robot.joints:
        t_local = robot_model.get_transform(
            frame_to=joint.child, frame_from=joint.parent,
        )
        trans = t_local[:3, 3]
        quat = Rotation.from_matrix(t_local[:3, :3]).as_quat()
        transforms.append(
            FrameTransform(
                parent_frame_id=joint.parent,
                child_frame_id=joint.child,
                translation=Vector3(
                    x=float(trans[0]), y=float(trans[1]), z=float(trans[2]),
                ),
                rotation=Quaternion(
                    x=float(quat[0]), y=float(quat[1]),
                    z=float(quat[2]), w=float(quat[3]),
                ),
            ),
        )
    return transforms


def _try_camera(cam_id: int | None, topic: str) -> tuple[Any, Any]:
    """Try to connect a camera; return (None, None) on failure or if not requested."""
    if cam_id is None:
        return None, None
    try:
        return _setup_camera(cam_id, topic)
    except Exception:
        logger.warning("Camera %s (device %d) failed", topic, cam_id, exc_info=True)
        return None, None


def _safe_publish(camera: Any, channel: Any) -> None:
    """Publish a camera frame, silently ignoring read errors."""
    if camera is None or channel is None:
        return
    try:
        _publish_frame(camera, channel)
    except Exception:
        logger.debug("Camera read failed", exc_info=True)


def main() -> None:
    """Entry point for ``python -m so101.foxglove_viz``."""
    args = _parse_args()

    import foxglove
    from foxglove.messages import FrameTransforms
    from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
    from yourdfpy import URDF

    foxglove.set_log_level(logging.INFO)

    urdf_path = Path(args.urdf)
    if not urdf_path.exists():
        logger.error("URDF not found: %s — clone foxglove-sdk SO101 example assets", urdf_path)
        sys.exit(1)

    robot_model = URDF.load(str(urdf_path))

    writer = None
    if args.write_mcap:
        mcap_path = args.mcap_path or (
            f"so101_{args.robot_id}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mcap"
        )
        writer = foxglove.open_mcap(mcap_path)
        logger.info("MCAP output: %s", mcap_path)

    server = foxglove.start_server()
    logger.info("Foxglove server: %s", server.app_url())

    wrist_cam, wrist_ch = _try_camera(args.wrist_cam_id, "wrist_image")
    env_cam, env_ch = _try_camera(args.env_cam_id, "env_image")

    config = SO101FollowerConfig(port=args.port, id=args.robot_id, use_degrees=True)
    follower = SO101Follower(config)
    follower.connect(calibrate=False)
    if not follower.is_connected:
        logger.error("Failed to connect to SO-101 on %s", args.port)
        sys.exit(1)
    follower.bus.disable_torque()

    joint_names = [j.name for j in robot_model.robot.joints]
    joint_positions: dict[str, float] = {name: 0.0 for name in joint_names}

    try:
        while True:
            _safe_publish(wrist_cam, wrist_ch)
            _safe_publish(env_cam, env_ch)
            _read_joints(follower.get_observation(), joint_positions)
            robot_model.update_cfg(joint_positions)
            foxglove.log("/tf", FrameTransforms(transforms=_build_transforms(robot_model)))
            time.sleep(1.0 / RATE_HZ)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server.stop()
        follower.disconnect()
        for cam in (wrist_cam, env_cam):
            if cam:
                cam.disconnect()
        if writer:
            writer.close()


if __name__ == "__main__":
    main()
