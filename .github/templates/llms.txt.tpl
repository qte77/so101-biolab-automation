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

- [so101/arms.py](${BLOB}/src/so101/arms.py): Dual SO-101 arm controller (LeRobot wrapper)
- [so101/pipette.py](${BLOB}/src/so101/pipette.py): Digital pipette serial control
- [so101/plate.py](${BLOB}/src/so101/plate.py): 96-well coordinate grid (SBS standard)
- [so101/tool_changer.py](${BLOB}/src/so101/tool_changer.py): Autonomous tool changing
- [so101/camera.py](${BLOB}/src/so101/camera.py): Multi-camera pipeline
- [so101/safety.py](${BLOB}/src/so101/safety.py): E-stop, watchdog, joint limits
- [dashboard/server.py](${BLOB}/src/dashboard/server.py): FastAPI remote oversight

## Configuration

- [configs/arms.yaml](${BLOB}/configs/arms.yaml): Arm port mappings and motor IDs
- [configs/plate_layout.yaml](${BLOB}/configs/plate_layout.yaml): Well coordinates and heights
- [configs/tool_dock.yaml](${BLOB}/configs/tool_dock.yaml): Tool dock station positions
