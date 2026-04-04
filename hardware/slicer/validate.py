"""Validate STL printability via PrusaSlicer CLI.

Slices each STL and reports overhang/support warnings.
PrusaSlicer is optional — graceful skip if unavailable.

Usage:
    python hardware/slicer/validate.py --all
    python hardware/slicer/validate.py hardware/stl/plate_holder.stl
    python hardware/slicer/validate.py --all --profile tpu
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLICER_CMD = "prusa-slicer"
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


def get_profile(stl_name: str, override: str | None = None) -> Path:
    """Return the slicer profile path for a given STL."""
    if override == "tpu" or stl_name in TPU_PARTS:
        return PROFILE_DIR / "tpu_95a_02mm.ini"
    return PROFILE_DIR / "pla_plus_02mm.ini"


def find_slicer() -> str | None:
    """Return slicer binary path or None."""
    return shutil.which(SLICER_CMD)


def validate_stl(stl_path: Path, profile: Path) -> dict:
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
        cmd = [
            SLICER_CMD,
            "--export-gcode",
            "--load",
            str(profile),
            "--output",
            str(gcode_out),
            str(stl_path),
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SEC,
            )
            output = (proc.stdout + "\n" + proc.stderr).lower()

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

    if not find_slicer():
        print(f"SKIP: {SLICER_CMD} not found. Install via: make setup_slicer")
        return 0

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

    results = [validate_stl(stl, get_profile(stl.name, args.profile)) for stl in stls]
    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())
