"""Compatibility guard for the lerobot monkey-patches in src/so101/cli/patch_lerobot.py.

## Why this test exists

`src/so101/cli/patch_lerobot.py` modifies the installed lerobot package via
exact-string replacement. The `ORIGINAL` / `PATCHED` constants must match
the lerobot source byte-for-byte. When lerobot is upgraded upstream (even
a whitespace or rename change), the patch script silently becomes a no-op
— users then hit the original mixed-firmware bugs with no obvious cause.

This test asserts that each patch's code block is still present in the
installed lerobot source (either the ORIGINAL form, for a clean venv, or
the PATCHED form, for a venv where the patches have already been applied).
If neither form is found, the test fails loudly with a pointer to which
constant needs updating.

## When this test runs

Marked `@pytest.mark.lerobot` — **excluded from `make test`** by default.
Only runs when you opt in:

    uv run pytest -m lerobot

Or after `uv sync --group lerobot`, typically as part of a pre-release
check or when bumping the lerobot pin. This avoids forcing every CI run
to install the heavy lerobot dependency tree (~400MB with torch, CUDA, etc.).

## Troubleshooting a failure

If this test fails after upgrading lerobot:
  1. Open the offending file in `.venv/lib/python.../site-packages/lerobot/`
  2. Compare the current source to the `ORIGINAL` constant in patch_lerobot.py
  3. Update the `ORIGINAL` (and matching `PATCHED`) strings to the new source
  4. Re-run `uv run so101-patch-lerobot` to re-apply against the new version
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.lerobot

# Skip the entire module if lerobot isn't installed — the test is meaningless
# without the files to inspect. `importorskip` produces a clean skip message
# rather than a confusing ImportError.
pytest.importorskip("lerobot")


class TestPatchLerobotCompat:
    """Assert that each patch's target code block still exists in lerobot source.

    Each test looks for EITHER the ORIGINAL form (unpatched venv) OR the
    PATCHED form (venv where `so101-patch-lerobot` has already run).
    A failure means lerobot upstream changed and the patch script needs
    updating before it can be applied.
    """

    def test_firmware_check_block_present(self) -> None:
        """_assert_same_firmware code block must match the patch script's expectation."""
        # Import here (not at module top) so import errors manifest as test
        # failures, not collection errors — keeps the skip-if-missing flow clean.
        from so101.cli.patch_lerobot import FEETECH_PY, FW_ORIGINAL, FW_PATCHED

        source = FEETECH_PY.read_text()
        assert FW_ORIGINAL in source or FW_PATCHED in source, (
            f"Neither ORIGINAL nor PATCHED block for _assert_same_firmware found in "
            f"{FEETECH_PY} — lerobot upstream has drifted. Update FW_ORIGINAL/FW_PATCHED "
            "in src/so101/cli/patch_lerobot.py to match the new source."
        )

    def test_sync_read_block_present(self) -> None:
        """_sync_read code block must match the patch script's expectation."""
        from so101.cli.patch_lerobot import MOTORS_BUS_PY, SYNC_ORIGINAL, SYNC_PATCHED

        source = MOTORS_BUS_PY.read_text()
        assert SYNC_ORIGINAL in source or SYNC_PATCHED in source, (
            f"Neither ORIGINAL nor PATCHED block for _sync_read found in "
            f"{MOTORS_BUS_PY} — lerobot upstream has drifted. Update "
            "SYNC_ORIGINAL/SYNC_PATCHED in src/so101/cli/patch_lerobot.py to match."
        )

    def test_calibration_write_block_present(self) -> None:
        """write_calibration code block must match the patch script's expectation."""
        from so101.cli.patch_lerobot import CAL_ORIGINAL, CAL_PATCHED, FEETECH_PY

        source = FEETECH_PY.read_text()
        assert CAL_ORIGINAL in source or CAL_PATCHED in source, (
            f"Neither ORIGINAL nor PATCHED block for write_calibration found in "
            f"{FEETECH_PY} — lerobot upstream has drifted. Update "
            "CAL_ORIGINAL/CAL_PATCHED in src/so101/cli/patch_lerobot.py to match."
        )
