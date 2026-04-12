"""96-well microplate coordinate grid (SBS standard).

SBS/ANSI standard: 127.76 x 85.48 mm footprint.
Well spacing: 9.0 mm center-to-center.
A1 origin: top-left corner (14.38 mm from left edge, 11.24 mm from top edge).
"""

from pydantic import BaseModel, ConfigDict

# SBS standard dimensions (mm)
WELL_SPACING = 9.0
A1_OFFSET_X = 14.38  # mm from left edge to A1 center
A1_OFFSET_Y = 11.24  # mm from top edge to A1 center
ROWS = "ABCDEFGH"
COLS = range(1, 13)


class WellPosition(BaseModel):
    """A single well position on a 96-well plate."""

    model_config = ConfigDict(strict=True, frozen=True)

    row: str  # A-H
    col: int  # 1-12
    x_mm: float  # mm from plate origin
    y_mm: float  # mm from plate origin

    @property
    def name(self) -> str:
        """Well name like 'A1', 'H12'."""
        return f"{self.row}{self.col}"


def well_coordinates(row: str, col: int) -> tuple[float, float]:
    """Get (x, y) coordinates in mm for a well position.

    Args:
        row: Row letter A-H.
        col: Column number 1-12.

    Returns:
        Tuple of (x_mm, y_mm) from plate origin.
    """
    row_idx = ROWS.index(row.upper())
    col_idx = col - 1
    x = A1_OFFSET_X + col_idx * WELL_SPACING
    y = A1_OFFSET_Y + row_idx * WELL_SPACING
    return (x, y)


def get_well(row: str, col: int) -> WellPosition:
    """Get a WellPosition for the given row and column.

    Args:
        row: Row letter A-H.
        col: Column number 1-12.

    Returns:
        WellPosition with coordinates.
    """
    x, y = well_coordinates(row, col)
    return WellPosition(row=row.upper(), col=col, x_mm=x, y_mm=y)


def all_wells() -> list[WellPosition]:
    """Get all 96 well positions in row-major order (A1, A2, ..., H12)."""
    return [get_well(row, col) for row in ROWS for col in COLS]


def parse_well_name(name: str) -> WellPosition:
    """Parse a well name like 'A1' or 'H12' into a WellPosition.

    Args:
        name: Well name string (e.g., 'A1', 'B12').

    Returns:
        WellPosition with coordinates.

    Raises:
        ValueError: If the well name is invalid.
    """
    name = name.strip().upper()
    if len(name) < 2 or name[0] not in ROWS:
        raise ValueError(f"Invalid well name: {name}")
    try:
        col = int(name[1:])
    except ValueError as err:
        raise ValueError(f"Invalid well name: {name}") from err
    if col < 1 or col > 12:
        raise ValueError(f"Column out of range: {col}")
    return get_well(name[0], col)
