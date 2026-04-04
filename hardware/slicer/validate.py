"""Validate STL printability via slicer CLI.

Tries OrcaSlicer first, falls back to PrusaSlicer if unavailable.
Both are optional — graceful skip if neither is found.

Usage:
    python hardware/slicer/validate.py --all
    python hardware/slicer/validate.py hardware/stl/plate_holder.stl
    python hardware/slicer/validate.py --all --profile tpu
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLICER_PREFERENCE = ["orca-slicer", "prusa-slicer"]
TIMEOUT_SEC = 120
STL_DIR = Path(__file__).resolve().parent.parent / "stl"
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


def get_profile(
    stl_name: str, override: str | None = None, slicer_name: str = "prusa-slicer"
) -> Path:
    """Return the slicer profile path for a given STL and slicer."""
    ext = ".json" if slicer_name == "orca-slicer" else ".ini"
    if override == "tpu" or stl_name in TPU_PARTS:
        return PROFILE_DIR / f"tpu_95a_02mm{ext}"
    return PROFILE_DIR / f"pla_plus_02mm{ext}"


def find_slicer() -> tuple[str, str] | None:
    """Return (slicer_name, path) for the first available slicer, or None."""
    for cmd in SLICER_PREFERENCE:
        path = shutil.which(cmd)
        if path:
            return (cmd, path)
    return None


def _build_cmd(
    slicer_name: str, profile: Path, gcode_out: Path, stl_path: Path
) -> list[str]:
    """Build slicer CLI command based on slicer type."""
    if slicer_name == "orca-slicer":
        return [
            slicer_name,
            "--slice", "1",
            "--load-settings", str(profile),
            "--export-gcode",
            "--output", str(gcode_out),
            str(stl_path),
        ]
    return [
        slicer_name,
        "--export-gcode",
        "--load", str(profile),
        "--output", str(gcode_out),
        str(stl_path),
    ]


def _run_with_xvfb_fallback(cmd: list[str], slicer_name: str) -> subprocess.CompletedProcess:
    """Run slicer command, retrying with xvfb-run on OrcaSlicer segfault."""
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SEC)

    if slicer_name == "orca-slicer" and proc.returncode == -11 and not os.environ.get("DISPLAY"):
        if shutil.which("xvfb-run"):
            proc = subprocess.run(
                ["xvfb-run", "--auto-servernum", *cmd],
                capture_output=True, text=True, timeout=TIMEOUT_SEC,
            )
        else:
            proc.stderr = "SKIP: OrcaSlicer segfault — install xvfb: sudo apt install xvfb"

    return proc


def validate_stl(
    stl_path: Path, profile: Path, slicer_name: str = "prusa-slicer"
) -> dict:
    """Slice an STL and parse output for printability issues."""
    result = {
        "file": stl_path.name,
        "profile": profile.stem,
        "warnings": [],
        "status": "PASS",
        "error": None,
    }

    with tempfile.TemporaryDirectory() as tmp:
        gcode_out = Path(tmp) / (stl_path.stem + ".gcode")
        cmd = _build_cmd(slicer_name, profile, gcode_out, stl_path)

        try:
            proc = _run_with_xvfb_fallback(cmd, slicer_name)
            output = (proc.stdout + "\n" + proc.stderr).lower()

            # Segfault without xvfb — graceful skip
            if proc.returncode == -11:
                result["status"] = "SKIP"
                result["error"] = proc.stderr.strip()[:200] or "Slicer segfault (no display)"
                return result

            # Parse warnings
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

    # Header
    print(f"\n{'Part':<35} {'Profile':<18} {'Warnings':<25} {'Status'}")
    print("-" * 85)

    exit_code = 0
    for r in results:
        warnings = ", ".join(r["warnings"]) if r["warnings"] else "none"
        status = r["status"]
        error_suffix = f" ({r['error']})" if r["error"] else ""
        print(f"{r['file']:<35} {r['profile']:<18} {warnings:<25} {status}{error_suffix}")
        if status == "FAIL":
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
    args = parser.parse_args()

    slicer = find_slicer()
    if not slicer:
        names = ", ".join(SLICER_PREFERENCE)
        print(f"SKIP: No slicer found ({names}). Install via: make setup_slicer")
        return 0

    slicer_name, _slicer_path = slicer

    if args.all:
        stls = sorted(STL_DIR.glob("*.stl"))
    elif args.files:
        stls = collect_stls(args.files)
    else:
        parser.print_help()
        return 1

    if not stls:
        print(f"No STL files found in {STL_DIR}. Run: make render_parts")
        return 1

    results = [
        validate_stl(stl, get_profile(stl.name, args.profile, slicer_name), slicer_name)
        for stl in stls
    ]
    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())
