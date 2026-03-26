# ${PROJECT_NAME}

> ${PROJECT_DESC}

## Documentation

- [README](${BLOB}/README.md)
- [AGENTS](${BLOB}/AGENTS.md)
- [CONTRIBUTING](${BLOB}/CONTRIBUTING.md)
- [Architecture](${BLOB}/docs/architecture.md)
- [User Stories](${BLOB}/docs/UserStory.md)
- [Demo Scenarios](${BLOB}/docs/demo-scenarios.md)
- [Hardware BOM](${BLOB}/docs/hardware/BOM.md)
- [CHANGELOG](${BLOB}/CHANGELOG.md)

## Source

- [biolab/arms.py](${BLOB}/src/biolab/arms.py): Dual SO-101 arm controller (LeRobot wrapper)
- [biolab/pipette.py](${BLOB}/src/biolab/pipette.py): Digital pipette serial control
- [biolab/plate.py](${BLOB}/src/biolab/plate.py): 96-well coordinate grid (SBS standard)
- [biolab/tool_changer.py](${BLOB}/src/biolab/tool_changer.py): Autonomous tool changing
- [biolab/camera.py](${BLOB}/src/biolab/camera.py): Multi-camera pipeline
- [biolab/safety.py](${BLOB}/src/biolab/safety.py): E-stop, watchdog, joint limits
- [dashboard/server.py](${BLOB}/src/dashboard/server.py): FastAPI remote oversight

## Configuration

- [configs/arms.yaml](${BLOB}/configs/arms.yaml): Arm port mappings and motor IDs
- [configs/plate_layout.yaml](${BLOB}/configs/plate_layout.yaml): Well coordinates and heights
- [configs/tool_dock.yaml](${BLOB}/configs/tool_dock.yaml): Tool dock station positions
