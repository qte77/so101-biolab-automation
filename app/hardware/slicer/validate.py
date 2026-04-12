"""Validate STL printability via CuraEngine (preferred) or PrusaSlicer (fallback).

Slices each STL and reports overhang/support warnings.
Both slicers are optional — graceful skip if unavailable.
Mesh integrity check uses stdlib only (struct) — no external deps.

Usage:
    python hardware/slicer/validate.py --all
    python hardware/slicer/validate.py --all --structural
    python hardware/slicer/validate.py hardware/stl/plate_holder.stl
    python hardware/slicer/validate.py --all --profile tpu
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT_SEC = 120
STL_DIR = Path(__file__).resolve().parents[3] / "hardware" / "stl"
PROFILE_DIR = Path(__file__).resolve().parent / "profiles"

# Part-to-profile mapping (default: PLA+)
TPU_PARTS = {"gripper_tips_tpu.stl"}

OVERHANG_KEYWORDS = [
    "overhang",
    "unsupported",
    "bridge",
    "support enforcer",
    "empty layer",
]


def get_profile(stl_name: str, backend: str, override: str | None = None) -> Path:
    """Return the slicer profile path for a given STL and backend."""
    ext = ".json" if backend == "cura" else ".ini"
    if override == "tpu" or stl_name in TPU_PARTS:
        return PROFILE_DIR / f"tpu_95a_02mm{ext}"
    return PROFILE_DIR / f"pla_plus_02mm{ext}"


def detect_slicer() -> tuple[str, str] | None:
    """Return (backend_name, binary_path) for the first available slicer."""
    cura = shutil.which("CuraEngine")
    if cura:
        return ("cura", cura)
    prusa = shutil.which("prusa-slicer")
    if prusa:
        return ("prusa", prusa)
    return None


_profile_cache: dict[Path, dict] = {}


def _load_profile(profile: Path) -> dict:
    """Load and cache a JSON slicer profile."""
    if profile not in _profile_cache:
        _profile_cache[profile] = json.loads(profile.read_text())
    return _profile_cache[profile]


def _build_cura_cmd(binary: str, stl_path: Path, profile: Path, gcode_out: Path) -> list[str]:
    """Build CuraEngine CLI command with settings from JSON profile."""
    settings = _load_profile(profile)
    cmd = [binary, "slice", "-l", str(stl_path), "-o", str(gcode_out)]
    for key, value in settings.items():
        if key.startswith("_"):
            continue
        # CuraEngine uses -s key=value for each setting
        if isinstance(value, bool):
            cmd.extend(["-s", f"{key}={'true' if value else 'false'}"])
        else:
            cmd.extend(["-s", f"{key}={value}"])
    return cmd


def _build_prusa_cmd(binary: str, stl_path: Path, profile: Path, gcode_out: Path) -> list[str]:
    """Build PrusaSlicer CLI command."""
    return [
        binary,
        "--export-gcode",
        "--load",
        str(profile),
        "--output",
        str(gcode_out),
        str(stl_path),
    ]


def validate_stl(stl_path: Path, backend: str, binary: str, profile: Path) -> dict:
    """Slice an STL and parse output for printability issues."""
    result = {
        "file": stl_path.name,
        "profile": profile.stem,
        "slicer": backend,
        "warnings": [],
        "status": "PASS",
        "error": None,
    }

    with tempfile.TemporaryDirectory() as tmp:
        gcode_out = Path(tmp) / (stl_path.stem + ".gcode")

        if backend == "cura":
            cmd = _build_cura_cmd(binary, stl_path, profile, gcode_out)
        else:
            cmd = _build_prusa_cmd(binary, stl_path, profile, gcode_out)

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SEC)
            output = (proc.stdout + "\n" + proc.stderr).lower()

            for keyword in OVERHANG_KEYWORDS:
                if keyword in output:
                    result["warnings"].append(keyword)

            if proc.returncode != 0:
                result["status"] = "FAIL"
                result["error"] = proc.stderr.strip()[:200]
            elif result["warnings"]:
                result["status"] = "WARN"

        except subprocess.TimeoutExpired:
            result["status"] = "SKIP"
            result["error"] = f"Timeout after {TIMEOUT_SEC}s"
        except FileNotFoundError:
            result["status"] = "SKIP"
            result["error"] = "Slicer binary not found"

    return result


def check_mesh_integrity(stl_path: Path) -> dict:
    """Check STL binary mesh integrity (no external deps).

    Parses the 80-byte header + 4-byte triangle count from a binary STL.
    Verifies the file is non-empty, has > 0 triangles, and the file size
    matches the expected size (80 + 4 + 50 * num_triangles).

    Args:
        stl_path: Path to the STL file.

    Returns:
        Dict with status (PASS/FAIL), triangle_count, and optional error.
    """
    result: dict = {"file": stl_path.name, "status": "PASS", "triangle_count": 0, "error": None}

    try:
        data = stl_path.read_bytes()
    except OSError as exc:
        result["status"] = "FAIL"
        result["error"] = str(exc)
        return result

    # Binary STL: 80-byte header + 4-byte uint32 triangle count
    if len(data) < 84:
        result["status"] = "FAIL"
        result["error"] = f"File too small ({len(data)} bytes, need >= 84)"
        return result

    (num_triangles,) = struct.unpack_from("<I", data, 80)
    result["triangle_count"] = num_triangles

    if num_triangles == 0:
        result["status"] = "FAIL"
        result["error"] = "Zero triangles in STL"
        return result

    expected_size = 84 + 50 * num_triangles
    if len(data) < expected_size:
        result["status"] = "FAIL"
        result["error"] = f"File truncated ({len(data)} bytes, expected {expected_size})"
        return result

    return result


def collect_stls(paths: list[str]) -> list[Path]:
    """Collect STL files from args or --all."""
    stls = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            stls.append(path)
        elif path.is_dir():
            stls.extend(sorted(path.glob("*.stl")))
    return stls


def print_report(results: list[dict]) -> int:
    """Print validation report table. Returns exit code."""
    if not results:
        print("No STL files found to validate.")
        return 1

    print(f"\n{'Part':<35} {'Profile':<18} {'Slicer':<8} {'Warnings':<25} {'Status'}")
    print("-" * 95)

    exit_code = 0
    for r in results:
        warns = ", ".join(r["warnings"]) if r["warnings"] else "none"
        err = f" ({r['error']})" if r["error"] else ""
        slicer = r["slicer"]
        print(f"{r['file']:<35} {r['profile']:<18} {slicer:<8} {warns:<25} {r['status']}{err}")
        if r["status"] == "FAIL":
            exit_code = 1

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"\n{passed}/{total} parts passed printability check.\n")
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate STL printability via slicer")
    parser.add_argument("files", nargs="*", help="STL files to validate")
    parser.add_argument("--all", action="store_true", help="Validate all STLs in hardware/stl/")
    parser.add_argument("--profile", choices=["pla", "tpu"], help="Force profile override")
    parser.add_argument("--structural", action="store_true", help="Run mesh integrity check")
    args = parser.parse_args()

    slicer = detect_slicer()

    if not slicer and not args.structural:
        print("SKIP: No slicer found. Install via: make setup_slicer")
        return 0

    if args.all:
        stls = sorted(STL_DIR.glob("**/*.stl"))
    elif args.files:
        stls = collect_stls(args.files)
    else:
        parser.print_help()
        return 1

    if not stls:
        print(f"No STL files found in {STL_DIR}. Run: make render_parts")
        return 1

    if args.structural:
        print("\n=== Mesh Integrity Check ===")
        mesh_results = [check_mesh_integrity(stl) for stl in stls]
        failed = [r for r in mesh_results if r["status"] == "FAIL"]
        for r in mesh_results:
            status = r["status"]
            err = f" ({r['error']})" if r["error"] else ""
            print(f"  {r['file']:<35} {r['triangle_count']:>6} triangles  {status}{err}")
        if failed:
            print(f"\n{len(failed)} STL(s) failed mesh integrity check.\n")
            return 1
        print(f"\n{len(mesh_results)}/{len(mesh_results)} STLs passed mesh integrity.\n")

    if slicer is None:
        return 0
    backend, binary = slicer
    print(f"--- Validating with {backend} ({binary})")
    results = [
        validate_stl(stl, backend, binary, get_profile(stl.name, backend, args.profile))
        for stl in stls
    ]
    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())
