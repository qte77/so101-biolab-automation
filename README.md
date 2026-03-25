# so101-biolab-automation

Dual SO-101 robotic arm bio-lab automation: 96-well pipetting, tool changing, remote oversight.

## What This Demonstrates

- **Teacher-student learning** — Leader arm teaches follower via imitation learning (ACT policy)
- **Coordinate commands** — Direct well-to-well pipetting by coordinate grid
- **Remote oversight** — WebRTC camera feeds + WebSocket command injection from browser
- **Tool changing** — Arms swap between pipette, gripper, and fridge hook autonomously

## Hardware

Two [SO-101](https://github.com/therobotstudio/so-arm100) follower arms + one leader arm, controlled via [LeRobot](https://huggingface.co/docs/lerobot). ~$400 total BOM. See `hardware/BOM.md` for details.

## Quick Start

```bash
# Setup
make setup

# Calibrate arms
make calibrate

# Teleoperate (teacher-student)
make teleop

# Record pipetting episodes
make record TASK="pipette row A"

# Train policy
make train

# Run demo
make demo
```

## Architecture

```
Remote Dashboard (FastAPI + WebRTC)
        │
Edge Controller (RPi 5 / Jetson)
  ├── LeRobot (teleop, policy, record)
  ├── PyLabRobot (pipette, 96-well layout)
  ├── Tool Changer (servo + magnet dock)
  └── Camera Pipeline (OpenCV → WebRTC)
        │
   Arm A (student) ── Arm B (teacher/student)
```

## Project Structure

```
src/biolab/        Core arm control, pipette, plate coords, tool changer, safety
src/dashboard/     FastAPI server, WebRTC video, browser UI
scripts/           Calibration, recording, training, demo orchestration
configs/           Arm ports, plate layout, tool dock positions
hardware/          BOM, STL files, wiring diagrams
tests/             Unit tests for plate coords, tool changer, safety
docs/              Assembly guide, demo scenarios, architecture
```

## Key Dependencies

- [LeRobot](https://github.com/huggingface/lerobot) — Teleoperation + imitation learning
- [PyLabRobot](https://github.com/PyLabRobot/pylabrobot) — Liquid handling abstractions
- [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2) — 3D-printed pipette reference
- FastAPI + WebRTC — Remote dashboard
- OpenCV — Camera pipeline

## License

Apache-2.0
