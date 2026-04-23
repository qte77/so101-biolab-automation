---
title: Demo Scenarios
purpose: Runnable commands and expected output for every use case (UC1-5)
authority: Operations (AUTHORITY)
created: 2026-03-27
updated: 2026-03-27
---

# Demo Scenarios

How to run and verify each use case (UC). All commands work in stub mode (no hardware).

## Prerequisites

```bash
make setup_all      # install all dependencies + tools
make serve          # (optional) start dashboard on :8080
```

**Physical demo setup (optional).** The pipetting use cases (UC1, UC5) can be demonstrated on real hardware once the printed parts and pipette are mounted. The DLAB dPette+ 8-channel mount is the primary configuration — see [../src/hardware/README.md](../src/hardware/README.md#dpette-8-channel-mount-replaces-so-101-gripper-jaws) for the assembly and print settings, [../docs/hardware/BOM.md](hardware/BOM.md) for the parts list, and [prusa-mk4-ops.md](hardware/prusa-mk4-ops.md) for uploading gcode to a Prusa MK4 via PrusaLink. All demo commands below also run cleanly in **stub mode** without any hardware.

## UC1: Pipette a 96-Well Plate

### UC1.1: Single Well

Aspirate 50 µL from trough, dispense to well A1.

```bash
uv run so101-demo --use-case uc1_single --well A1 --volume 50
```

Expected output:

```text
[UC1] Move arm_a → TROUGH (200.0, 0.0 mm)
[UC1] Aspirate 50.0 µL
Moving arm_a to well A1 (14.38, 11.24 mm)
[UC1] Dispense 50.0 µL → A1
Demo complete.
```

### UC1.2: Row

Pipette all 12 wells in row A at 25 µL each.

```bash
uv run so101-demo --use-case uc1_row --row A --volume 25
```

Expected: 12 aspirate/dispense cycles (A1 through A12).

### UC1.3: Column

Pipette all 8 wells in column 1 at 20 µL each.

```bash
uv run so101-demo --use-case uc1_col --col 1 --volume 20
```

Expected: 8 aspirate/dispense cycles (A1 through H1).

### UC1.4: Full Plate

Pipette all 96 wells at 20 µL each.

```bash
uv run so101-demo --use-case uc1_full --volume 20
```

Expected: 96 aspirate/dispense cycles. Each well gets an independent aspirate→dispense so the pipette never overflows its 200 µL capacity.

## UC2: Fridge Operations

Open fridge with hook tool, swap to gripper, grab item, move to park.

```bash
uv run so101-demo --use-case uc2
```

Expected output:

```text
[UC2] Starting fridge sequence
Tool changed to fridge_hook
[UC2] Approach fridge
[UC2] Engage hook — pull door
[UC2] Release hook — door open
Tool changed to gripper
[UC2] Grab item from fridge
Parking arm arm_a
Parking arm arm_b
[UC2] Fridge sequence complete — item at park position
```

## UC3: Tool Interchange

Cycle through all tools: pipette → gripper → fridge hook → gripper.

```bash
uv run so101-demo --use-case uc3
```

Expected output:

```text
[UC3] Starting tool cycle: ['pipette', 'gripper', 'fridge_hook', 'gripper']
[UC3] Equipped pipette
[UC3] Equipped gripper
[UC3] Equipped fridge_hook
[UC3] Equipped gripper
```

## UC4: Full Demo (All Use Cases)

Runs UC1.1 + UC1.2 (row A) + UC1.2 (column 1) + UC2 + UC3 in sequence.

```bash
uv run so101-demo
```

Or equivalently:

```bash
uv run so101-demo --use-case all
```

## Dashboard Demo

Start the dashboard and trigger the workflow via WebSocket:

```bash
make serve_dashboard
```

Open `http://localhost:8080` in a browser. Click "Run Demo" button. The full UC4 sequence runs in the background. Check `GET /api/status` for current state.

Or via curl:

```bash
# Check status
curl http://localhost:8080/api/status

# Trigger e-stop via WebSocket (using websocat)
echo '{"command": "e_stop"}' | websocat ws://localhost:8080/ws
```

## Verification

All scenarios are covered by automated tests:

```bash
uv run pytest tests/test_workflow.py -v    # workflow use case tests
uv run pytest tests/test_dashboard.py -v   # dashboard integration tests
uv run pytest -q                           # full suite
```
