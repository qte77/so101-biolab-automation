---
title: "Outlook: Ceiling-Mounted SO-101 on Linear Rail"
purpose: Feasibility study for inverted SO-101 arm on ceiling gantry — mechanical, software, safety
authority: Research (INFORMATIONAL — not requirements)
created: 2026-04-12
updated: 2026-04-12
---

# Outlook: Ceiling-Mounted SO-101 on Linear Rail

## Concept

Mount an SO-101 arm inverted from a ceiling-mounted linear rail, freeing the
entire bench surface. The arm approaches plates, Bento Lab, and reagents from
above — a natural orientation for pipetting and plate handling.

## Mechanical Feasibility

STS3215 servos (30 kg-cm Pro, 1:345 gear reduction) can handle inverted
operation, with caveats:

- **Backlash amplification** — gravity pulls through gear backlash zones
  instead of preloading against them, increasing end-effector positional error.
- **Sustained holding torque** — base and shoulder servos see continuous load
  rather than intermittent peaks.
- **3D-printed joint stress** — PLA/PETG joints designed for compression loads
  experience tension/hanging loads when inverted. Shoulder joint is the
  critical failure point.

### Required Modifications

- Metal base plate (aluminum or carbon fiber)
- Metal shoulder bracket
- Anti-backlash spring on wrist
- Secure bolt fasteners replacing press-fits
- Safety cable/lanyard to rail (redundant fall protection)

## Rail / Gantry Options

| System | Payload | Span | Drive | Cost (1 m) | Python Control |
|--------|---------|------|-------|------------|----------------|
| OpenBuilds C-Beam + XLarge cart | ~5 kg | ~2 m | GT2 belt | ~$80-150 | `grbl-streamer` (PyPI) or `pyserial` |
| igus drylin W | 5-15 kg | 3 m | Belt / lead screw | ~$150-300 | `pymodbus` (ModbusTCP) — no SDK |
| Bosch Rexroth aluminum | 10+ kg | 3 m+ | Rack-and-pinion | ~$300-600 | PLC integration only |

### Controller Options

| Controller | Interface | Python Package | Notes |
|------------|-----------|----------------|-------|
| OpenBuilds BlackBox (Grbl) | USB serial 115200 | `grbl-streamer` | Standard G-code |
| xPro V5 (FluidNC/ESP32) | USB + WiFi + WebSocket | `pyserial` / `websockets` | YAML config, REST + WebSocket API |
| ODrive | USB/CAN | `odrive` (PyPI v0.6.11) | Async Python, brushless servo |
| Moteus | CAN-FD/USB | `moteus` (PyPI v0.3.99) | Async Python, position/velocity/torque |
| Klipper `manual_stepper` | USB serial | `moonraker-api` (PyPI) | Reuse Klipper stack for single axis |

**Recommendation:** OpenBuilds C-Beam + FluidNC on ESP32. G-code + WebSocket +
Python via `grbl-streamer`, with community precedent for non-CNC linear motion.

## Workspace Advantages

- Eliminates arm bench footprint entirely.
- Reach envelope shifts from hemisphere-above-table to downward-facing cone.
- Collision avoidance simplifies — arm approaches from above, not around
  obstacles at bench level.
- Rail axis extends reach beyond a single arm's work envelope.

## Software Impact

- **URDF:** Rotate base link 180 deg around Y-axis. DH parameters unchanged.
- **Gravity compensation:** Sign flip on virtual displacement direction. See
  phospho.ai gravity compensation guide for SO-100/101.
- **IK:** `lerobot-kinematics` (box2ai-robotics) provides IK for SO-100;
  gravity vector changes but joint geometry is identical.
- **ACT policies:** Do NOT transfer from tabletop to inverted — joint angle
  distributions and gravity dynamics differ. Requires new teleoperation
  demonstrations with arm inverted.
- **SafetyMonitor:** Existing `JOINT_LIMITS` in `safety.py` apply, but limits
  should be re-validated for inverted loading.
- **XZGantry interaction:** Ceiling rail may replace or complement the existing
  XZ gantry (ceiling = long axis, gantry = cross axis).

## Safety Considerations

- **Falling risk:** Primary hazard. Redundant mechanical fastening (bolts +
  safety cable). STS3215 servos have no brake — arm free-falls on power loss.
  Mitigate with spring-return or counterweight.
- **E-stop:** Must cut servo power AND engage mechanical brake or friction lock.
- **Vibration:** Belt-driven movement transmits vibration. Pause and settle
  after gantry moves before pipetting. Rubber isolator mount plate recommended.
- **Drip risk:** Inverted arm above open containers — any debris/lubricant
  falls into samples. Use enclosed cable routing and drip shields.

## Precedents

- **Yamaha YK-XGS** — purpose-built ceiling-mount SCARA (industrial).
- **UR cobots** — officially support floor, wall, and ceiling mounting with
  software installation angle parameter.
- **Yaskawa HC cobots** — inverted mounting with 180 deg mount angle setting.
- No documented SO-101/SO-100 inverted mounting found (this would be novel).

## Quick Refs

| Ref | URL |
|-----|-----|
| SO-101 docs (HuggingFace) | <https://huggingface.co/docs/lerobot/so101> |
| SO-ARM100 (TheRobotStudio) | <https://github.com/TheRobotStudio/SO-ARM100> |
| Gravity compensation (phospho.ai) | <https://docs.phospho.ai/learn/gravity-compensation> |
| lerobot-kinematics | <https://github.com/box2ai-robotics/lerobot-kinematics> |
| Inverted robots overview | <https://www.robots.com/blogs/topsy-turvy-invert-mounted-robots> |
| Yamaha YK-XGS ceiling SCARA | <https://global.yamaha-motor.com/business/robot/lineup/ykxg/hang_inverse/> |
| Yaskawa HC inverted arm | <https://knowledge.motoman.com/hc/en-us/articles/23505485971991-HC-Robots-Wall-Mounted-or-Inverted-Arm-Control> |
| OpenBuilds V-Slot gantry carts | <https://us.openbuilds.com/gantry-carts-kits/> |
| OpenBuilds Python serial thread | <https://builds.openbuilds.com/threads/python-serial-communication-with-blackbox.18451/> |
| FluidNC (ESP32 Grbl) | <https://github.com/bdring/FluidNC> |
| FluidNC WebSocket docs | <http://wiki.fluidnc.com/en/support/interface/websockets> |
| FluidNC Web API | <http://wiki.fluidnc.com/en/features/WebAPI> |
| grbl-streamer (PyPI) | <https://pypi.org/project/grbl-streamer/> |
| ODrive Python (PyPI) | <https://pypi.org/project/odrive/> |
| Moteus Python (PyPI) | <https://pypi.org/project/moteus/> |
| TMC2209-PY (PyPI) | <https://pypi.org/project/TMC2209-PY/> |
| Klipper manual_stepper config | <https://www.klipper3d.org/Config_Reference.html> |
| moonraker-api (PyPI) | <https://pypi.org/project/moonraker-api/> |
| igus drylin actuators | <https://www.igus.com/drylin-e/turnkey-linear-actuators> |
| igus Robot Control (iRC) | <https://www.igus.co.uk/info/robot-software> |
| ROS ceiling mounting discussion | <https://answers.ros.org/question/321902/mounting-robot-arm-from-ceiling/> |
