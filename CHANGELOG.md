# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/), [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial project scaffold: dual-arm controller, pipette, plate coords, tool changer, safety, dashboard
- 96-well SBS coordinate grid with full test coverage
- Tool changer state machine with magnetic dock abstraction
- Safety monitor with watchdog, e-stop, joint limits
- FastAPI dashboard with WebSocket command channel
- LeRobot integration for SO-101 teleoperation and recording
