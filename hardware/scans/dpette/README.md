# dPette+ 3D Scan Reference Data

Source mesh used to redesign the dPette+ 8-channel mount geometry
(`app/hardware/cad/dpette/dpette_multi_handle.py` + `dpette_ejector_lever.py`).

## Files

| File | Size | Format | Source |
|---|---|---|---|
| `0410_02_mesh.ply` | ~2.3 MB | Stanford PLY (binary) | Revopoint 3D scan, 2026-04-10 |
| `0410_02_mesh.stl` | ~4.6 MB | Binary STL (derived) | PLY → STL conversion |

## Scale & Coordinates

- **1:1 mm** — no scaling applied
- Origin and axes match Revopoint scanner output (no re-orientation)

## Intended use

Reference geometry for parametric rebuilds of dPette+-specific parts.
Not meant to be 3D printed directly — use the parametric build123d
scripts in `app/hardware/cad/dpette/` for printable parts.

## Provenance

Captured by Antonio Lamb (@antomicblitz) and incorporated via PR #48.
Preserved here as-is under the project's Apache-2.0 license (same as
the rest of the repo).
