# PrusaLink API Reference — Prusa MK4

Printer: **Original Prusa MK4** (PrusaLink 2.1.2, API 2.0.0)
Host: `192.168.1.86` / `prusa-mk4.local`
Serial: `10589-3742441633503380`
Auth: HTTP Digest (`maker` / see `~/prusa_mk4_pw`)

## Endpoints

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/version` | API/firmware version, nozzle diameter, capabilities |
| GET | `/api/v1/info` | Printer serial, nozzle, MMU status, min extrusion temp |

### Printer Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/status` | Live printer state, bed/nozzle temps, axis positions, fan speeds, job progress |

### Job Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/job` | Current job details (file, progress %, time elapsed) |
| DELETE | `/api/v1/job/{id}` | Cancel/stop a running print |
| PUT | `/api/v1/job/{id}/pause` | Pause a running print |
| PUT | `/api/v1/job/{id}/resume` | Resume a paused print |

### Storage

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/storage` | List storage devices (USB only on this printer) |

### File Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/files/usb` | List all files/folders on USB |
| PUT | `/api/v1/files/usb/{filename}` | Upload gcode file (binary body) |
| DELETE | `/api/v1/files/usb/{filename}` | Delete a file |
| POST | `/api/v1/files/usb/{filename}` | Start print (`{"command":"start"}`) |

### Transfer

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/transfer` | File transfer status |
| DELETE | `/api/v1/transfer/{id}` | Cancel active transfer |

### Cameras

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cameras` | List active cameras |
| GET | `/api/v1/cameras/snap` | Capture from default camera |
| GET | `/api/v1/cameras/{id}/snap` | Capture from specific camera |
| POST | `/api/v1/cameras/{id}/snap` | Take manual snapshot |
| POST | `/api/v1/cameras/{id}` | Setup or fix a camera |
| DELETE | `/api/v1/cameras/{id}` | Delete a camera |
| PATCH | `/api/v1/cameras/{id}/config` | Update camera settings |

## Headers

| Header | Value | Description |
|--------|-------|-------------|
| `Content-Type` | `application/octet-stream` | Required for PUT upload |
| `Print-After-Upload` | `?1` or `?0` | Auto-start print after upload |

## Examples

```bash
# Check printer status
curl -s --digest -u "maker:$PRUSA_PW" http://192.168.1.86/api/v1/status

# Upload gcode
curl -s --digest -u "maker:$PRUSA_PW" \
  -X PUT -H "Content-Type: application/octet-stream" \
  --data-binary @mypart.gcode \
  http://192.168.1.86/api/v1/files/usb/mypart.gcode

# Upload and print immediately
curl -s --digest -u "maker:$PRUSA_PW" \
  -X PUT -H "Content-Type: application/octet-stream" \
  -H "Print-After-Upload: ?1" \
  --data-binary @mypart.gcode \
  http://192.168.1.86/api/v1/files/usb/mypart.gcode

# Start a print
curl -s --digest -u "maker:$PRUSA_PW" \
  -X POST -H "Content-Type: application/json" \
  -d '{"command":"start"}' \
  http://192.168.1.86/api/v1/files/usb/MYPART~1.GCO

# Cancel current print
curl -s --digest -u "maker:$PRUSA_PW" \
  -X DELETE http://192.168.1.86/api/v1/job/294

# Delete a file from USB
curl -s --digest -u "maker:$PRUSA_PW" \
  -X DELETE http://192.168.1.86/api/v1/files/usb/OLDFILE~1.GCO

# List USB files
curl -s --digest -u "maker:$PRUSA_PW" http://192.168.1.86/api/v1/files/usb
```

## CAD-to-Print Pipeline

```
build123d (.py) → STL → PrusaSlicer → .gcode → PrusaLink PUT → print
```

Parts live in `hardware/stl/dpette/` and `hardware/stl/so101/` (generated assets). CAD sources live in `app/hardware/cad/` (build123d is the primary backend).

Key printable parts:

| STL | Material | Notes |
|-----|----------|-------|
| `dpette_handle.stl` | PLA+ | U-bracket mount, single-channel |
| `dpette_multi_handle.stl` | PLA+ | U-bracket mount, 8-channel (Ø32mm split-bore clamp for DLAB dPette+) |
| `dpette_ejector_lever.stl` | PLA+ | Tip ejection lever for 8-channel pipette |

Slicer profile: `app/hardware/slicer/profiles/prusa_mk4_pla_02mm.ini`
Generate gcode: `prusa-slicer --load app/hardware/slicer/profiles/prusa_mk4_pla_02mm.ini --export-gcode -o output.gcode hardware/stl/dpette/<part>.stl`

## Notes

- Only **USB** storage is writable; `local` returns 403
- Uploaded `.gcode` files appear with 8.3 short names (e.g., `DPETTE~1.GCO`)
- The `display_name` field in responses shows the original filename
- Nozzle: 0.40mm, no MMU, min extrusion temp: 170C
- Capabilities: `upload-by-put: true`
