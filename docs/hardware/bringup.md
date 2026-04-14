# SO-101 Hardware Bringup Guide

Step-by-step procedure for bringing up the SO-101 dual-arm system.
Tested on Fedora 43, Python 3.12, lerobot 0.4.4.

> **Variant:** For a simplified 2-axis pipetting setup (shoulder_pan +
> shoulder_lift only, fixed electronic pipette mount), see
> [two-dof-pipette.md](two-dof-pipette.md).

## Prerequisites

- SO-101 arms assembled (2 followers + 1 leader), STS3215 servos, Waveshare serial bus servo driver boards
- USB-C cables connecting each Waveshare board to the PC
- 5V 4A power supplies connected and powered on
- `uv sync --group lerobot` completed (installs lerobot[feetech])

## 1. Serial Port Permissions

The Waveshare boards register as `/dev/ttyACM*` devices owned by the `dialout` group.

### Add user to dialout group

```bash
sudo usermod -aG dialout $USER
```

Requires **full re-login** to take effect (not just a new terminal).
`newgrp dialout` only affects the current shell, not subprocesses like `uv run`.

### Per-session alternative (no reboot)

```bash
sudo chmod 666 /dev/ttyACM0 /dev/ttyACM1 /dev/ttyACM2
```

Run this for **every connected arm** at the start of each session.

> **Note:** Resets on unplug/replug. For persistence, use a udev rule:
>
> ```bash
> sudo sh -c 'echo "SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"1a86\", MODE=\"0666\"" > /etc/udev/rules.d/99-waveshare.rules'
> sudo udevadm control --reload-rules && sudo udevadm trigger
> ```

## 2. USB Enumeration

### Find ports

```bash
uv run lerobot-find-port
```

Interactive: lists ports, asks you to **unplug** the USB cable, press Enter, then detects which port disappeared.

### Verify with servo scan

```python
from scservo_sdk import PortHandler, PacketHandler

port = PortHandler("/dev/ttyACM0")
port.openPort()
port.setBaudRate(1000000)
ph = PacketHandler(0)

for sid in range(21):
    model, result, error = ph.ping(port, sid)
    if result == 0:
        print(f"ID {sid}: model={model} err={error}")

port.closePort()
```

Expected output for one arm: 6 servos (IDs 1-6), model 777 (STS3215).

### Port assignments

| Arm | Default Port | Makefile Variable |
|-----|-------------|-------------------|
| Leader | `/dev/ttyACM0` | `LEADER_PORT` |
| Follower A | `/dev/ttyACM1` | `FOLLOWER_A_PORT` |
| Follower B | `/dev/ttyACM2` | `FOLLOWER_B_PORT` |

> **Tip:** Port numbers depend on USB plug order, not physical slot. They shift
> on replug. Always verify with `ls /dev/ttyACM*` and the servo scan. If teleop
> has the wrong arm moving, swap the ports.

## 3. Firmware Version Check

LeRobot requires all servos on the same firmware version. If versions differ, `lerobot-calibrate` will fail:

```
RuntimeError: Some Motors use different firmware versions:
{1: '3.10', 2: '3.9', 3: '3.10', 4: '3.10', 5: '3.10', 6: '3.10'}
```

### Option A: Flash mismatched servo (proper fix, requires Windows)

Firmware flashing uses a proprietary bootloader protocol — **no Linux tool exists**.
The `scservo_sdk` / `feetech-servo-sdk` only do register read/write, not firmware upload.

1. Get a Windows machine or VM with USB passthrough
2. Download FD software + firmware binary from <https://www.feetechrc.com/software>
3. **Disconnect all other servos** from the daisy chain — firmware flashing
   cannot address by ID, it uses a power-cycle bootloader handshake
4. Connect only the mismatched servo to the Waveshare board
5. Flash via FD tool
6. Reconnect all servos and verify

### Option B: Patch lerobot (prototyping only)

Mixed firmware causes **two** problems in lerobot 0.4.4:

1. `_assert_same_firmware()` raises `RuntimeError` blocking startup
2. `sync_read` fails with `[TxRxResult] Incorrect status packet!` — firmware
   3.9 returns a slightly different packet format that corrupts batch responses

Individual servo reads (`read2ByteTxRx`) work fine for all servos including 3.9.
The issue is only with sync (batch) reads across the shared bus.

The patch script fixes both:

```bash
uv run so101-patch-lerobot           # apply
uv run so101-patch-lerobot --revert  # restore
```

Or via Makefile: `make patch_lerobot` / `make patch_lerobot_revert`.

What it does:

- **Firmware check:** warns instead of raising `RuntimeError`
- **sync_read:** falls back to sequential individual reads when batch read fails
  (firmware 3.9 returns a different packet format that corrupts batch responses;
  individual reads work fine for all servos including 3.9)
- **Calibration clamp:** clamps range values to 0-4095 before writing to servo
  EPROM (glitchy reads via sign-magnitude decoding can produce negatives like -170,
  which the servo rejects)

This patches the **installed** lerobot package in-place (under `.venv/`).
The patch is overwritten by `uv sync` — re-run the script after reinstalling.

> **Warning:** Sequential reads are slower than sync reads. This is acceptable
> for calibration and prototyping but may add latency during teleoperation.
> For production use, flash all servos to the same firmware version (Option A).

## 4. Pre-calibration Checklist

Before calibrating any arm:

1. **Permissions:** `sudo chmod 666 /dev/ttyACM*` (or udev rule)
2. **Patches:** `uv run so101-patch-lerobot` (if mixed firmware)
3. **Power:** 5V 4A supply connected and on for each Waveshare board
4. **Verify servos:** Run the servo scan script (section 2) to confirm 6 servos respond

## 5. Calibrate Leader Arm

```bash
uv run lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM0 \
  --teleop.id=leader
```

> **Important:** Leader arms use `--teleop.*` flags, not `--robot.*`.

### Calibration prompts

The calibration will ask you to move joints to the **middle of their range of motion**.
Use this as a reference for the neutral pose:

| Joint | Description | Middle position |
|-------|-------------|-----------------|
| 1 | Base rotation | Arm pointing straight forward |
| 2 | Shoulder | ~45°, halfway between up and horizontal |
| 3 | Elbow | ~90°, forearm halfway bent |
| 4 | Wrist pitch | Level / neutral |
| 5 | Wrist roll | Centered, no rotation |
| 6 | Gripper | Half open |

Put the arm in a relaxed, neutral pose — not at any extreme — then press Enter.

After the midpoint, you'll be asked to move each joint through its full range
(min to max). Move slowly and smoothly.

Calibration data is saved to `~/.cache/huggingface/lerobot/calibration/leader/`.

## 6. Calibrate Follower Arms

```bash
# Follower A
uv run lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM1 \
  --robot.id=arm_a

# Follower B
uv run lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM2 \
  --robot.id=arm_b
```

Or use the Makefile target (calibrates all three sequentially):

```bash
make calibrate_arms
```

## 7. Teleoperation Test (Grippers)

After calibration, test leader-follower teleoperation.

### Identify ports with multiple arms

`lerobot-find-port` fails with multiple boards plugged in:

```
OSError: Could not detect the port. More than one port was found (['/dev/ttyACM1', '/dev/ttyACM0'])
```

Use `ls /dev/ttyACM*` instead. Port assignment depends on plug order, not
physical slot. If unsure which is leader vs follower, try one — if the arms
are swapped, flip the ports.

### Run teleoperation

```bash
sudo chmod 666 /dev/ttyACM0 /dev/ttyACM1
uv run lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM1 \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM0
```

Or via Makefile:

```bash
make start_teleop
```

Verify the follower arm mirrors the leader's movements.

## 8. Pipette Holder Swap

After grippers are working:

1. Print pipette holders (see [app/hardware/README.md](../../app/hardware/README.md) for parts list and print settings)
2. Mount holders on follower arm(s)
3. Re-calibrate if gripper-to-holder swap changes joint offsets
4. Test tool changer cycle: return gripper, pick up holder

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Permission denied: '/dev/ttyACM0'` | User not in `dialout` group | `sudo chmod 666 /dev/ttyACM*` or add to group + re-login |
| `newgrp dialout` doesn't help | Only affects current shell, not `uv run` subprocesses | Use `chmod 666` or udev rule instead |
| `lerobot-find-port` finds nothing | Didn't unplug cable during prompt | Unplug USB, press Enter, replug when told |
| `lerobot-find-port` multiple ports | Multiple boards plugged in | Use `ls /dev/ttyACM*` instead |
| `invalid choice: 'so101_leader'` for `--robot.type` | Leader uses `--teleop.type`, not `--robot.type` | Use `--teleop.type=so101_leader` |
| Firmware version mismatch | Servos on different FW versions | `uv run so101-patch-lerobot` or flash with FD |
| `Incorrect status packet!` on sync_read | FW 3.9 corrupts batch responses | Patch script adds sequential fallback |
| `Negative values are not allowed` | Glitchy read → negative via sign-magnitude decode | Patch script adds calibration clamp |
| `Input voltage error!` | Transient servo error during rapid reads | Patch script suppresses; check power if persistent |
| `Missing motor IDs` (all 6) | Power supply unplugged/off | Connect 5V 4A supply to Waveshare board |
| `Missing motor IDs` (some) | Servo overload/error lockout or loose cable | Power-cycle the 5V supply, reseat daisy-chain cables |
| Motor LED blinking during teleop | Servo error (overload/position) | Power-cycle; may indicate port swap (follower treated as leader) |
| Leader arm stuck / won't move by hand | Ports swapped — leader has torque on | Swap `--robot.port` and `--teleop.port` |
| `Mismatch between calibration values` | Patched clamp values differ from JSON | Press Enter to use saved calibration — this is expected |
| Teleop: `--robot.id` / `--teleop.id` missing | IDs default to None, can't find calibration | Always pass `--robot.id=arm_a --teleop.id=leader` |
| Same min and max during calibration | Joints not moved, or glitchy reads | Move each joint fully; ensure patch is applied |
| Port number shifted | USB re-enumeration on replug | `ls /dev/ttyACM*`; `sudo chmod 666` again |
| Gripper not following during teleop | Narrow calibration range on leader gripper | Re-calibrate with full gripper open/close range |
| Gripper servo LED blinking | Overload error — commanded to out-of-range position | Power-cycle 5V supply; check if gripper moves freely by hand when off |
| Servo overload after calibration mismatch | Leader/follower gripper ranges don't align | Re-calibrate both arms' grippers with matching full range |
