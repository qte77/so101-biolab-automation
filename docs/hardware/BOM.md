---
title: Bill of Materials
purpose: Hardware shopping list with first-party vendor links and cost estimates
authority: Hardware (AUTHORITY)
created: 2026-03-27
updated: 2026-04-11
validated_links: 2026-03-27
---

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

**Custom parts:**

| Part | Status | Source | Material | Notes |
|------|--------|--------|----------|-------|
| Pipette mount adapter | Designed | `cad/so101/pipette_mount.py` | PLA+ | dPette barrel clamp for SO-101 wrist |
| Tool dock (3-station) | Designed | `cad/so101/tool_dock.py` | PLA+ | Magnetic dock, ref: [Berkeley tool changer](https://goldberg.berkeley.edu/pubs/CASE2018-ron-tool-changer-submitted.pdf) |
| Tool cones (robot/pipette/gripper) | Designed | `cad/so101/tool_changer.py` | PLA+ | Passive tool changer cones |
| Compliant gripper tips | Designed | `cad/so101/gripper_tips.py` | TPU 95A | Ref: [silicone mold (Thingiverse)](https://www.thingiverse.com/thing:7152864), [fin-ray gripper (MakerWorld)](https://makerworld.com/en/models/2075813) |
| 96-well plate holder | Designed | `cad/labware/plate_holder.py` | PLA+ | SBS footprint alignment pins |
| Tip rack holder | Designed | `cad/labware/tip_rack_holder.py` | PLA+ | Holds standard pipette tip rack |
| dPette single cradle | Designed | `cad/dpette/dpette_cradle.py` | PLA+ | Rest cradle for AELAB dPette 7016 |
| dPette multi cradle | Designed | `cad/dpette/dpette_cradle.py` | PLA+ | Rest cradle for DLAB dPette+ 8-channel |
| Tip ejection post | Designed | `cad/dpette/tip_ejection_bar.py` | PLA+ | Fixed post — arm pushes ejector button onto post to pop tips |
| dPette handle (U-bracket mount) | Designed | `cad/dpette/dpette_handle.py` | PLA+ | Single-channel dPette mount for SO-101 (M5 horn → barrel clamp) |
| dPette cam arm | Designed | `cad/dpette/dpette_handle.py` | PLA+ | Straight radial arm on M6 horn — sweeps into ejector hook |
| dPette tip release station | Designed | `cad/dpette/dpette_tip_release.py` | PLA+ | L-bracket ejector + waste slot, universal single/multi-channel |
| dPette+ 8-ch mount (split-bore clamp) | Designed | `cad/dpette/dpette_multi_handle.py` | PLA+ | Ø32mm split-bore clamp replacing SO-101 bottom jaw — **derived from 1:1 mm Revopoint scan** (`hardware/scans/dpette/`) |
| dPette+ ejector lever | Designed | `cad/dpette/dpette_multi_handle.py` | PLA+ | M6-horn-mounted lever replacing SO-101 top jaw — ~175N @ 20mm arm |
| Fridge hook end-effector | Designed (deferred) | `cad/so101/fridge_hook.py` | PLA+ | Hook for fridge door handle |
| XZ gantry frame | Designed (deferred) | `cad/deferred/xz_gantry_frame.py` | PLA+ | XZ gantry structural frame |
| XZ carriage pipette dock | Designed (deferred) | `cad/deferred/xz_carriage.py` | PLA+ | XZ gantry carriage with pipette dock |

## 3D Printer (for custom parts)

| Part | ~Cost | Source | Notes |
|------|-------|--------|-------|
| [Original Prusa MK4](https://www.prusa3d.com/product/original-prusa-mk4s-3d-printer/) | ~$800 kit / ~$1,100 assembled | Prusa Research | Nextruder + input shaper. PrusaLink HTTP API + MK4 slicer profiles bundled at `src/hardware/slicer/profiles/prusa_mk4_*.ini`. See [prusa-mk4-ops.md](prusa-mk4-ops.md) for the API reference and upload / print curl examples. |
| PLA+ filament (1 kg) | $20–25 | [Prusament PLA](https://www.prusa3d.com/product/prusament-pla-prusa-galaxy-black-1kg-nfc/) or generic | Default material for functional parts |
| TPU 95A filament (0.5 kg) | $25 | Generic | Only for `gripper_tips_tpu.stl` |
| 0.4mm nozzle | — | included with MK4 | Default profile targets 0.4mm |

**Alternative printers** supported by the slicer pipeline: any PrusaSlicer-compatible printer. Pipeline is slicer-agnostic — swap profiles to target a different machine without code changes. Bambu Lab printers remain the target for the future camera + VLM agent-loop step (see [roadmap.md](../roadmap.md)).

## 3D Scanner (for scan-informed CAD, optional)

| Part | ~Cost | Source | Notes |
|------|-------|--------|-------|
| [Revopoint MINI 2](https://www.revopoint3d.com/products/industry-3d-scanner-mini) or similar | $450–900 | Revopoint | Structured-light scanner for capturing physical parts as reference geometry. Output PLY/STL at 1:1 mm. See `hardware/scans/dpette/` for the dPette+ handle scan that drove the `dpette_multi_handle` redesign. |

Scanner is **optional** — most parts are purely parametric. Scan-informed design is useful for fitting custom mounts to off-the-shelf hardware with complex curved geometry (pipettes, grips, handles).

## Cameras

| Part | Qty | ~Cost | Source |
|------|-----|-------|--------|
| 32x32mm UVC camera module (wrist) | 2 | $15 ea | Per [SO-ARM100 wrist camera options](https://github.com/TheRobotStudio/SO-ARM100#5-wristmount-cameras) |
| USB webcam 1080p (overhead) | 1 | $25 | Per [SO-ARM100 overhead mount](https://github.com/TheRobotStudio/SO-ARM100#2-overhead-camera-mount) |

## Commercial Electronic Pipettes (Primary)

| Part | Qty | ~Cost | Source | Notes |
|------|-----|-------|--------|-------|
| AELAB dPette 7016 (single-channel, 0.5–10,000 µL) | 1 | ~$200 | AELAB | USB port — protocol TBD (see `ElectronicPipette` backend) |
| DLAB dPette+ (8-channel, 0.5–300 µL) | 1 | ~$600 | DLAB | USB port — protocol TBD (same approach) |
| Pipette tips (compatible with dPette) | 1 box ea | $15 ea | Lab supply | |

## Digital Pipette (DIY Alternative)

Based on [digital-pipette-v2](https://github.com/ac-rad/digital-pipette-v2)
([paper: RSC Digital Discovery 2026](https://pubs.rsc.org/en/content/articlehtml/2026/dd/d5dd00336a)).

| Part | Qty | ~Cost | Source |
|------|-----|-------|--------|
| 1mL syringe (Luer slip) | 5 | $5 | Lab supply |
| Linear actuator L16-50-63-6-R (5cm stroke) | 1 | $70 | [Actuonix (manufacturer)](https://www.actuonix.com/l16-50-63-6-r) |
| Arduino Nano | 1 | $5 | [Arduino store](https://store.arduino.cc/products/arduino-nano) |
| 3D-printed pipette body | 1 | — | [STL + code](https://github.com/ac-rad/digital-pipette-v2) |
| Pipette tips (1-200 uL) | 1 box | $15 | Lab supply |

## XZ Gantry (Dedicated Pipetting Arm)

Simpler alternative to SO-101 for repetitive pipetting at fixed positions.

| Part | Qty | ~Cost | Source |
|------|-----|-------|--------|
| MGN12 linear rail (200mm) | 2 | $15 ea | AliExpress / Amazon |
| NEMA 17 stepper motor | 2 | $10 ea | Generic |
| GT2 timing belt + pulleys | 1 set | $8 | Generic |
| Pololu Maestro 6-ch USB servo controller | 1 | $18 | [Pololu](https://www.pololu.com/product/1350) |
| *Alternative:* Raspberry Pi Pico W | 1 | $6 | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-pico/) |
| 3D-printed frame + carriage | 1 | ~$5 | Custom STL (see hardware parts issue) |

Estimated total: ~$60-80

## PCR Equipment

| Part | Qty | ~Cost | Source | Notes |
|------|-----|-------|--------|-------|
| [Bento Lab](https://www.bento.bio/) (portable PCR) | 1 | ~$1,500 | Bento Bioworks | Centrifuge + thermocycler + gel electrophoresis. USB control TBD. |

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
| Full SO-101 (2 followers + 1 leader, RPi, DIY pipette, cameras) | ~$650 |
| Full SO-101 + Jetson (GPU training on-device) | ~$820 |
| Full SO-101 + Prusa MK4 (for on-site custom part iteration) | ~$1,450 |
| XZ gantry only (dedicated pipetting, commercial pipettes) | ~$860 (gantry ~$60 + dPette 7016 ~$200 + dPette+ ~$600) |
| Full system (SO-101 + XZ gantry + Bento Lab + MK4) | ~$4,000+ |
| Full system + Revopoint scanner (scan-informed CAD workflow) | ~$4,500+ |
