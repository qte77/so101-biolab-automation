# Bill of Materials

Hardware shopping list for the so101-biolab-automation prototype.

Prices are estimates as of March 2026. Servo specs and gear ratios per
[SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100#parts-for-two-arms-follower-and-leader-setup).
Leader arm motor mapping per
[LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101#step-by-step-assembly-instructions).

## Arms (2x follower + 1x leader)

| Part | Qty | ~Cost | Source |
|------|-----|-------|--------|
| STS3215 Servo 7.4V, 1/345 gear (C001) | 13 | $14 ea | [Feetech STS3215 (Alibaba)](https://www.alibaba.com/product-detail/Feetech-STS3215-30KG-Serial-Bus-Servo_1601097543776.html), [Seeed Studio](https://www.seeedstudio.com/STS3215-30KG-Serial-Servo-p-6340.html) |
| STS3215 Servo 7.4V, 1/191 gear (C044) | 2 | $14 ea | Same — leader joints 1, 3 ([gear ratio table](https://huggingface.co/docs/lerobot/so101#step-by-step-assembly-instructions)) |
| STS3215 Servo 7.4V, 1/147 gear (C046) | 3 | $14 ea | Same — leader joints 4, 5, 6 |
| Waveshare Serial Bus Servo Driver Board | 3 | $11 ea | [Waveshare wiki](https://www.waveshare.com/wiki/Bus_Servo_Adapter) |
| USB-C Cable | 3 | $4 ea | Generic |
| 5V 4A DC Power Supply (5.5x2.1mm) | 3 | $10 ea | Generic |
| Table Clamp | 6 | $3 ea | Generic |
| Screwdriver Set (Phillips #0, #1) | 1 | $6 | Generic |

**Or buy assembled kits** (per [SO-ARM100 vendor list](https://github.com/TheRobotStudio/SO-ARM100#kits)):

- [Seeed Studio](https://www.seeedstudio.com/so-arm100-Standard-Kit-p-6329.html) — international, 3D printed kits
- [PartaBot](https://www.partabot.com/) — US, assembled versions
- [WowRobo](https://www.wowrobo.com/) — international, assembled versions

## 3D Printed Parts

Print settings per [SO-ARM100 printing guide](https://github.com/TheRobotStudio/SO-ARM100#printing-the-parts):
PLA+, 0.4mm nozzle, 0.2mm layer, 15% infill, supports >45 degrees.

| Part | Source |
|------|--------|
| Follower arm (all parts, single plate) | [SO-ARM100 STL (follower)](https://github.com/TheRobotStudio/SO-ARM100/tree/main/STL/SO101) |
| Leader arm (all parts, single plate) | [SO-ARM100 STL (leader)](https://github.com/TheRobotStudio/SO-ARM100/tree/main/STL/SO101) |

**Custom parts (to be designed for this project):**

| Part | Planned File | Material | Notes |
|------|-------------|----------|-------|
| Pipette mount adapter | *TBD* | PLA+ | Adapts gripper to hold digital-pipette-v2 |
| Tool dock (3-station) | *TBD* | PLA+ | Magnetic dock, ref: [Berkeley tool changer](https://goldberg.berkeley.edu/pubs/CASE2018-ron-tool-changer-submitted.pdf) |
| Fridge hook end-effector | *TBD* | PLA+ | Hook for fridge door handle |
| 96-well plate holder | *TBD* | PLA+ | SBS footprint alignment pins |
| Tip rack holder | *TBD* | PLA+ | Holds standard pipette tip rack |
| Compliant gripper tips | *TBD* | TPU 95A | Ref: [silicone mold (Thingiverse)](https://www.thingiverse.com/thing:7152864), [fin-ray gripper (MakerWorld)](https://makerworld.com/en/models/2075813) |

## Cameras

| Part | Qty | ~Cost | Source |
|------|-----|-------|--------|
| 32x32mm UVC camera module (wrist) | 2 | $15 ea | Per [SO-ARM100 wrist camera options](https://github.com/TheRobotStudio/SO-ARM100#5-wristmount-cameras) |
| USB webcam 1080p (overhead) | 1 | $25 | Per [SO-ARM100 overhead mount](https://github.com/TheRobotStudio/SO-ARM100#2-overhead-camera-mount) |

## Digital Pipette

Based on [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2)
([paper: RSC Digital Discovery 2026](https://pubs.rsc.org/en/content/articlehtml/2026/dd/d5dd00336a)).

| Part | Qty | ~Cost | Source |
|------|-----|-------|--------|
| 1mL syringe (Luer slip) | 5 | $5 | Lab supply |
| Linear actuator L16-50-63-6-R (5cm stroke) | 1 | $70 | [Actuonix (manufacturer)](https://www.actuonix.com/l16-50-63-6-r) |
| Arduino Nano | 1 | $5 | [Arduino store](https://store.arduino.cc/products/arduino-nano) |
| 3D-printed pipette body | 1 | — | [STL + code](https://github.com/ac-rad/digital-pipette-v2) |
| Pipette tips (1-200 uL) | 1 box | $15 | Lab supply |

## Edge Compute

| Option | Cost | Source | Notes |
|--------|------|--------|-------|
| Raspberry Pi 5 (8GB) | $80 | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-5/) | LeRobot inference, no GPU training |
| Jetson Orin Nano (8GB) | $250 | [nvidia.com](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/) | GPU for on-device ACT policy training |
| microSD 64GB+ | $10 | Generic | |
| USB hub (4+ ports) | $15 | Generic | 3 motor boards + cameras |

LeRobot supports both platforms per [LeRobot docs](https://huggingface.co/docs/lerobot/index).
Seeed Studio offers [reComputer Jetson + SO-101 kits](https://wiki.seeedstudio.com/lerobot_so100m/).

## Lab Consumables

| Part | Qty | ~Cost | Notes |
|------|-----|-------|-------|
| 96-well microplate (SBS, flat bottom) | 5 | $20 | [SBS/ANSI standard](https://en.wikipedia.org/wiki/Microplate#Standards): 127.76 x 85.48 mm, 9mm spacing |
| Reagent trough (25mL, SBS footprint) | 2 | $10 | Lab supply |
| Colored water / food dye | — | $5 | For demo visualization |

## Cost Summary

| Config | Estimated Cost |
|--------|----------------|
| Minimum (1 follower + 1 leader, RPi, no pipette) | ~$350 |
| Full prototype (2 followers + 1 leader, RPi, pipette, cameras) | ~$650 |
| With Jetson (GPU training on-device) | ~$820 |
