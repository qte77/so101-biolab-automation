---
title: CAD, Slicer & Simulation Tooling
purpose: CAD library decisions, slicer CLI comparison, SO-101 simulation stacks, STL build status
authority: Research (INFORMATIONAL — not requirements)
created: 2026-03-27
updated: 2026-04-12
---

# CAD, Slicer & Simulation Tooling

## CAD Library Comparison

**Problem:** CadQuery generates geometrically correct STLs but has no FDM awareness. Vertical empty rows, unsupported overhangs, and gravity failures are invisible until a print fails.

| Feature | CadQuery | Build123d | OpenSCAD | JSCAD | FreeCAD | Blender (bpy) |
|---------|----------|-----------|----------|-------|---------|----------------|
| Language | Python | Python | Own syntax | JavaScript | GUI + Python | Python |
| Paradigm | Parametric, BREP | Parametric, BREP | CSG only | CSG only | Full CAD | Mesh-based |
| Output | STEP, STL, DXF | STEP, STL | STL only | STL, OBJ | STEP, STL, many | STL, OBJ, many |
| Curve quality | Excellent | Excellent | Faceted | Faceted | Excellent | Mesh |
| For 3D printing | Great | Great | Common | OK | Great | Needs cleanup |
| For mechanical parts | Best in class | Very good | Limited | Limited | Best in class | Not ideal |
| Learning curve | Medium | Low-Medium | Low | Low | High | High |
| Browser-based | No | No | No | Yes | No | No |
| Open source | Yes | Yes | Yes | Yes | Yes | Yes |
| Python 3.13+ support | No (VTK blocked) | Yes | N/A | N/A | Yes | Yes |

**Decision (2026-04):** Migrating from CadQuery to **build123d** — same BREP kernel (OCP), lower learning curve, algebraic operators (`+`/`-` instead of `.union()`/`.cut()`), and builds on Python 3.13 where CadQuery's VTK dependency does not.

## OpenSCAD CLI

Mature, stable parametric CAD. `.scad` -> STL/SVG/DXF/PNG via CLI.

```bash
openscad -o out.stl input.scad                    # export STL
openscad -o out.svg --projection=ortho input.scad  # export SVG
openscad -D 'length=100' -o out.stl input.scad     # parametric override
openscad -p params.json -P set_name -o out.stl input.scad  # parameter file
```

- Install: `apt install openscad`, snap, flatpak, or AppImage
- CSG maps 1:1 from CadQuery: `box`->`cube`, `cylinder`->`cylinder`, `cut`->`difference()`, `revolve`->`rotate_extrude()`
- No printability validation (must pair with slicer)

## Slicer CLI Comparison

| Tool | CLI Maturity | Headless Linux | Overhang Detection | Notes |
|------|-------------|----------------|-------------------|-------|
| **PrusaSlicer** | Mature | Yes | Yes | `prusa-slicer --export-gcode model.stl --load config.ini`. Most stable. [Wiki](https://github.com/prusa3d/PrusaSlicer/wiki/Command-Line-Interface) |
| **Bambu Studio** | Modern | Yes (Docker avail) | Yes | `--slice`, `--orient`, `--arrange`, JSON config. Best error codes. [Wiki](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage) |
| **SuperSlicer** | Mature | Yes | Enhanced | PrusaSlicer fork with better overhang detection. [Docs](https://docs.superslicer.org/advanced-usage-guides/cmd-line-guide/) |
| **CuraEngine** | Stable | Yes | Limited | Pure engine, no GUI deps. JSON settings. [GitHub](https://github.com/Ultimaker/CuraEngine) |
| **OrcaSlicer** | **Broken** | **No** (GTK3 crashes) | Yes (when it works) | CLI shares GUI code, segfaults headless. [#2714](https://github.com/OrcaSlicer/OrcaSlicer/issues/2714), [#12277](https://github.com/OrcaSlicer/OrcaSlicer/issues/12277) |

**OrcaSlicer CLI root cause:** wxWidgets 3.1.7 (GTK3 backend) initializes display context even in CLI mode. Stack: `libslic3r` (core, decoupled) -> `libslic3r_gui` (wxWidgets) -> single binary. Fork lineage: Slic3r -> PrusaSlicer -> Bambu Studio -> OrcaSlicer (all share `libslic3r` core).

**Recommendation:** PrusaSlicer CLI for validation (stable, proven). Keep slicer-agnostic so Bambu Studio or SuperSlicer can substitute.

## SO-101 Simulation & Digital Twin

**Goal:** Catch hardware problems in software. Shift-left testing for robotics.

**Official SO-101 sim models:** URDF + MJCF at [TheRobotStudio/SO-ARM100/Simulation/SO101](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101). Includes `so101_new_calib.urdf`, `so101_new_calib.xml` (MuJoCo), `scene.xml`, joint properties, mesh assets. Generated via onshape-to-robot.

### Simulation Stacks

| Stack | Physics | GPU | SO-101 Tasks | Headless CI | Use for |
|-------|---------|-----|-------------|------------|---------|
| [MuJoCo](https://mujoco.readthedocs.io/) direct | MuJoCo 3.0+ | No | Via URDF/MJCF | Yes (`MUJOCO_GL=osmesa`) | CI tests, lightweight sim, control dev |
| [LeIsaac](https://github.com/LightwheelAI/leisaac) | Isaac Lab | Yes | `PickOrange`, `LiftCube`, `CleanToyTable`, `FoldCloth-BiArm` | Cloud (NVIDIA Brev) | Teleoperation, data collection, policy training |
| [ManiSkill](https://github.com/haosulab/ManiSkill) | SAPIEN | Yes | Via custom robot loading | Limited | RL training, GPU-parallelized (200k+ FPS) |
| [gym_hil](https://github.com/huggingface/gym-hil) | MuJoCo | No | Panda only (extensible) | Yes | Human-in-the-loop RL |

**LeIsaac details:**

- Official LeRobot EnvHub integration by [LightwheelAI](https://lightwheelai.github.io/leisaac/)
- SO101 follower + leader teleoperation in sim
- HDF5 -> LeRobot dataset conversion built-in
- Cloud sim: no local GPU required via NVIDIA Brev
- Usage: `make_env("LightwheelAI/leisaac_env:envs/so101_pick_orange.py", n_envs=1, trust_remote_code=True)`

**MuJoCo in CI (headless GitHub Actions):**

- Set `MUJOCO_GL=osmesa` for software rendering (no GPU, no X11)
- Install: `sudo apt-get install libosmesa6-dev`
- Proven pattern: MuJoCo official CI, openai/mujoco-py, community SO-100 sim

**OpenSCAD STL -> MuJoCo collision mesh:**

- Export binary STL from OpenSCAD -> reference in MJCF `<mesh>` tag
- MuJoCo auto-converts to convex hull for collision (sufficient for simple parts)
- Works for plate holders, tool changer cones, dock — may need simplification for complex geometry

### Sim-to-Real

- [lerobot-sim2real](https://github.com/StoneT2000/lerobot-sim2real): train in ManiSkill, deploy zero-shot to real SO-101
- GR00T-N1.5 policy fine-tuning on SO-101 via LeIsaac sim data
- Domain randomization (colors, textures, dynamics) for robust transfer
- Community SO-100 MuJoCo: [lachlanhurst/so100-mujoco-sim](https://github.com/lachlanhurst/so100-mujoco-sim) with Qt GUI + LeRobot sync

### Digital Twin for 3D Print Inspection

- Real-time layer-by-layer CNN inspection for over/under-extrusion ([MDPI 2025](https://www.mdpi.com/2075-1702/13/6/448))
- Zero-shot multi-criteria inspection via digital twin ([arXiv 2511.23214](https://arxiv.org/abs/2511.23214))
- 3D Gaussian Splatting for photorealistic rendering of printed parts
- [Systematic review: Digital Twins in 3D Printing](https://arxiv.org/html/2409.00877v1)

**Recommendation:**

1. **CI testing now:** MuJoCo + OSMesa (no GPU, headless, free)
2. **Policy training later:** LeIsaac when GPU available (or NVIDIA Brev cloud)
3. **Print inspection future:** Prototype with real camera + simulated geometry comparison

## XLeRobot Reference

[XLeRobot](https://github.com/Vector-Wangel/XLeRobot) — dual SO-101 mobile platform ($660, <4h assembly).

- Uses STEP + 3MF workflow (no code-generated CAD)
- Distributes STEP files for modification, STL/3MF for printing
- Addresses gravity/support via documentation + manual slicer orientation
- Z-axis scaling in slicer for fit adjustments (not in CAD)
- No automated printability checking
- Proves slicer-based workflow is viable for SO-101 ecosystem

## Validation Pipeline (Planned)

```text
OpenSCAD (.scad) --> STL --> PrusaSlicer CLI --> printability report
```

- OpenSCAD: parametric generator (reliable CLI, SVG via projection) — archived under `src/hardware/scad/`
- PrusaSlicer / CuraEngine: printability validator (optional, graceful fallback if unavailable)
- build123d: primary CAD backend in `src/hardware/cad/` (migrated from CadQuery 2026-04; scan-informed CAD delivered 2026-04-11)
- **PrusaLink API**: first concrete printer-API integration — see [`prusa-mk4-ops.md`](prusa-mk4-ops.md) for MK4 endpoint reference and curl examples

## STL Files Status

See [`src/hardware/parts.json`](../../src/hardware/parts.json) for the machine-readable manifest and [`src/hardware/README.md`](../../src/hardware/README.md) for the assembly guide. All parts are rendered via `make render_parts` (build123d primary, OpenSCAD fallback) into top-level `hardware/stl/`.

As of 2026-04-11:

- **11 legacy parts** (tool changer system, pipette mount, plate holder, tip rack holder, gripper tips, dPette cradles, tip ejection bar) — all ported to build123d in Phase 2, rendered at `hardware/stl/{so101,labware,dpette}/`
- **5 new dPette+ parts** from Antonio's PR #48 (ported to build123d):
  - `dpette_handle` / `dpette_cam_arm` — U-bracket single-channel mount (M5 horn -> dPette 7016 barrel)
  - `dpette_tip_release` — L-bracket tip ejector station, universal single/multi-channel
  - `dpette_multi_handle` / `dpette_ejector_lever` — 32mm split-bore 8-channel clamp replacing SO-101 gripper jaws, **derived from a 1:1 mm Revopoint scan** (see `hardware/scans/dpette/`)

**Print settings:** PLA+ default, 0.4mm nozzle, 0.2mm layer, 15% infill (25% for functional mounts). TPU 95A for gripper tips only. Prusa MK4 profiles available in `src/hardware/slicer/profiles/prusa_mk4_*.ini`.

**Design philosophy:** STL files are generated programmatically from build123d parametric scripts — reproducible, parametric, version-controlled. OpenSCAD scripts under `src/hardware/scad/` are archived as a fallback. Scan-derived geometry (Revopoint or similar) is captured at 1:1 mm in `hardware/scans/`; the parts.json `scan_source` field provides queryable provenance.
