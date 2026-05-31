---
title: "Outlook: Perception — LIDAR, depth sensing, and digital twin"
purpose: Landscape survey of 3D sensing options (LIDAR, depth, photogrammetry) and BIM/digital-twin integration for spatial awareness in the agentic biolab.
authority: Research (INFORMATIONAL — not requirements)
created: 2026-05-31
updated: 2026-05-31
---

# Outlook: Perception — LIDAR, depth sensing, and digital twin

## Concept

The agentic system today operates on **pre-taught named positions only**. It
has no sense of whether the deck still matches what was taught, whether a
plate has shifted, whether an operator's hand is in the swept volume, or — at
the larger scale — where it is in the lab. This document surveys the sensor
and software stacks that could close that gap, separates them by spatial
scale, and records relevance / feasibility for this repo.

Two distinct scales are in scope. They do **not** share a sensor class or a
software stack and should be treated as independent tracks:

| Track | Scale | Use case | Sensor class | Map representation |
|-------|-------|----------|--------------|--------------------|
| (a) Workcell | ≤ 500 mm | Pre-move clearance, deck-state check, operator-hand safety | Short-range depth (structured light / ToF) + fiducials | Small URDF / USD scene with bounding boxes |
| (b) Lab-room | 3-15 m | Mobile-base navigation, multi-station routing, layout digital twin | 360° LIDAR + IMU (SLAM) | Georeferenced point cloud → USD / IFC |

Tracking issues: **#perc-a** (workcell), **#perc-b** (lab-room).

## Reference projects analyzed

### OpenScan — <https://openscan.eu>

Open-source **photogrammetry** scanner: turntable + camera + Raspberry Pi.
Generates dense meshes of small objects (cm scale).

- **Relevance:** Low for surroundings awareness. OpenScan is object-scale, fully
  offline, takes minutes per scan. Useful only as a tool to digitize one-off
  labware (custom cradles, 3D-printed adapters) into the URDF/USD scene used by
  track (a).
- **Feasibility:** Trivial — it is a self-contained appliance, not an integration.
  Output is STL/OBJ that feeds the existing `tools/cad/` pipeline.

### `github.com/topics/3d-lidar` — survey topic

Aggregator for LIDAR-related repos. Content is dominated by autonomous-driving
stacks (Autoware, Apollo, KITTI tooling) and outdoor mapping.

- **Relevance:** Low directly, but the topic surfaces the indoor SLAM subset
  (FAST-LIO, Point-LIO, GLIM, HBA, MAD-ICP) that is the actual reference for
  track (b).
- **Feasibility:** Not a project — a discovery surface. Use it to pick the SLAM
  backend once a LIDAR is on a mobile base.

### MANDEYE — <https://github.com/januszbedkowski/mandeye_controller>

Handheld Livox Mid-360 + IMU logger, MIT-licensed. Companion project
**HDMapping** (`MapsHD/HDMapping`) processes the logs offline into
georeferenced point clouds.

- **Relevance:** High for track (b). It is the closest published reference to
  what a single lab-mapping pass would look like: walk the room with the sensor
  once, post-process, get a static prior the agent localizes against. Sensor
  choice (Livox Mid-360) and the data-collection-then-post-process split are
  both directly applicable.
- **Feasibility:** Hardware ~$1.5k for the Livox Mid-360 alone. Build effort
  is ~1-2 weeks for hardware + a first usable map. **Not justified until there
  is a mobile platform to localize.**

## Sensor-class summary

| Class | Example | Range | Min range | Cost | Fits track |
|-------|---------|-------|-----------|------|-----------|
| Structured-light depth | Intel RealSense D405 | 7-50 cm | 7 cm | ~$580 | (a) |
| ToF depth | Orbbec Femto Bolt / Mega | 0.25-5 m | ~25 cm | ~$400 | (a) (with caveats on min range) |
| Stereo + NN | Luxonis OAK-D SR | 0.2-2 m | 20 cm | ~$300 | (a) |
| Solid-state LIDAR | Livox Mid-360 | 0.1-40 m | 10 cm | ~$1,500 | (b) |
| Solid-state LIDAR | Unitree L1 / L2 | 0.1-30 m | 10 cm | ~$700-1,000 | (b) |
| Photogrammetry rig | OpenScan | cm-scale | n/a | DIY | one-off labware digitization |

LIDAR is the **wrong tool** for track (a). 10 cm minimum range covers most of
the SO-101 reach envelope as a dead zone, and angular resolution at 30 cm is
too coarse to resolve a tip rack edge. Depth cameras are the **wrong tool**
for track (b): FOV is too narrow for room-scale mapping in one pass.

## Track (a): workcell awareness — feasibility

- **Sensor:** RealSense D405 is the strongest fit. 7 cm minimum range, designed
  for short-range manipulation, well-supported (`pyrealsense2` on PyPI), used in
  the existing LeRobot ecosystem.
- **Software:** New `src/so101/perception/` module behind a `DepthSource`
  Protocol. ArUco / AprilTag (`opencv-contrib-python`) anchors deck and
  labware. `perception/deck_model.py` holds a small URDF or USD scene that the
  orchestrator queries via `is_clear(from, to)` before each scripted move.
- **Integration:** Composition over `DualArmController` and the orchestrator
  added in qte77/i3mega-pipettebot#120. Opt-in via `SO101_PERCEPTION=on`;
  default off, so existing behavior is preserved.
- **Test strategy:** Recorded depth frames + synthetic fiducial fixtures in
  `tests/perception/`. No hardware-gated tests in CI; live tests tagged
  `@pytest.mark.hardware`.
- **Effort:** ~1 week for driver + fiducial pipeline + first clearance check.
- **Blocking risk:** None. Depth cam is a $580 dependency; the rest is code.

## Track (b): lab-room SLAM + digital twin — feasibility

- **Sensor:** Livox Mid-360 (primary candidate) or Unitree L1/L2 (cheaper
  fallback). 360° × ~59° FOV, 40 m range, 10 cm min range — sized for indoor.
- **Data pipeline:**
  1. MANDEYE-style logger captures Livox frames + IMU during a single walk-around.
  2. HDMapping (or FAST-LIO / GLIM) post-processes to a georeferenced cloud.
  3. Conversion step: point cloud → USD scene (preferred — matches the Isaac /
     MuJoCo workflows already in the roadmap) or IFC (true BIM interop via
     IfcOpenShell, heavier dep tree).
  4. `perception/world_model.py` loads the scene at startup; planner consults
     it for waypoints and forbidden volumes.
  5. Online localization against the prior map (FAST-LIO2 odometry). SLAM on
     the fly only as a fallback.
- **BIM angle:** Worth distinguishing.
  - **USD digital twin** — pragmatic, code-friendly, what robotics tools speak.
  - **IFC / BIM** — useful only if the lab's facility-management data already
    lives in IFC, or if floor-plan handoff to other building systems is needed.
    Default to USD; treat IFC as a separate export.
- **Blocking risk:** Hard block on the existence of a mobile platform. With a
  fixed bench, track (a) covers the entire collision-relevant volume; (b) adds
  cost without unlocking new behavior. **Trigger to unblock:** first PR that
  introduces a wheeled base, gantry-on-rails, or AMR integration. Re-evaluate
  sensor choice at that point — the Livox / Unitree market moves quickly.
- **Effort:** ~1-2 weeks once unblocked, dominated by SLAM tuning and the
  USD/IFC conversion.

## 3D-printed mounts and fixtures

Both tracks need printed parts (sensor brackets, fiducial holders, calibration
targets). These live in the existing `src/hardware/` + `tools/cad/` pipeline —
no new tooling required. Track (a) needs a D405 bracket sized to the SO-101
wrist or to a fixed overhead pole; track (b) needs a Livox + IMU enclosure for
the MANDEYE-style logger. Mass and obstruction budget should be reviewed
against the existing payload limits before committing a design.

## Decision summary

- **Do now:** Track (a), gated by issue #perc-a.
- **Defer:** Track (b), captured in issue #perc-b, blocked on mobile platform.
- **Reject (for surroundings awareness):** Photogrammetry as a runtime sensor.
  Keep OpenScan in mind only for one-off labware digitization.

## Quick Refs

| Ref | URL |
|-----|-----|
| OpenScan | <https://openscan.eu> |
| 3D LIDAR topic | <https://github.com/topics/3d-lidar> |
| MANDEYE controller | <https://github.com/januszbedkowski/mandeye_controller> |
| HDMapping | <https://github.com/MapsHD/HDMapping> |
| FAST-LIO2 | <https://github.com/hku-mars/FAST_LIO> |
| GLIM | <https://github.com/koide3/glim> |
| Livox Mid-360 | <https://www.livoxtech.com/mid-360> |
| Unitree LIDAR | <https://shop.unitree.com/products/unitree-lidar> |
| Intel RealSense D405 | <https://www.intelrealsense.com/depth-camera-d405/> |
| Orbbec Femto Bolt | <https://www.orbbec.com/products/tof-camera/femto-bolt/> |
| Luxonis OAK-D SR | <https://shop.luxonis.com/products/oak-d-sr> |
| pyrealsense2 (PyPI) | <https://pypi.org/project/pyrealsense2/> |
| OpenCV ArUco docs | <https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html> |
| OpenUSD | <https://openusd.org/> |
| IfcOpenShell | <https://ifcopenshell.org/> |
| MuJoCo | <https://mujoco.org/> |
| Isaac Sim | <https://developer.nvidia.com/isaac/sim> |
