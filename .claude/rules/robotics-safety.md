# Robotics Safety

**Project-specific rules for robotic arm automation.**

## Hardware Safety

- **Never bypass SafetyMonitor** — all arm operations must be supervised by watchdog
- **Never hardcode joint positions** — use YAML configs (`configs/*.yaml`)
- **Never skip stub mode fallback** — every hardware module must degrade gracefully when its dependency is unavailable
- **Never send actions without joint limit checks** — validate against JOINT_LIMITS before commanding real hardware

## Arm Operations

- **LeRobot API only** — never bypass the `DualArmController` abstraction for arm commands
- **Park before disconnect** — always call `park_all()` before `disconnect()`
- **One config per parameter** — serial ports, joint limits, dock positions live in YAML, not code

## Pipette Safety

- **Track fill state** — never allow aspirate beyond `max_volume_ul` or dispense beyond `_current_fill`
- **Validate volumes** — reject zero, negative, or overflow volumes before actuating

## Tool Changing

- **Verify tool state** — `changer.current_tool` must reflect physical state
- **Return before pickup** — always return current tool to dock before picking up a new one
