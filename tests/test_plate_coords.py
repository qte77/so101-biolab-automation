"""Tests for 96-well plate coordinate calculations."""

import pytest

from biolab.plate import (
    A1_OFFSET_X,
    A1_OFFSET_Y,
    WELL_SPACING,
    all_wells,
    get_well,
    parse_well_name,
    well_coordinates,
)


class TestWellCoordinates:
    """Test well coordinate calculations against SBS standard."""

    def test_a1_coordinates(self) -> None:
        x, y = well_coordinates("A", 1)
        assert x == pytest.approx(A1_OFFSET_X)
        assert y == pytest.approx(A1_OFFSET_Y)

    def test_a12_coordinates(self) -> None:
        x, y = well_coordinates("A", 12)
        assert x == pytest.approx(A1_OFFSET_X + 11 * WELL_SPACING)
        assert y == pytest.approx(A1_OFFSET_Y)

    def test_h1_coordinates(self) -> None:
        x, y = well_coordinates("H", 1)
        assert x == pytest.approx(A1_OFFSET_X)
        assert y == pytest.approx(A1_OFFSET_Y + 7 * WELL_SPACING)

    def test_h12_coordinates(self) -> None:
        x, y = well_coordinates("H", 12)
        assert x == pytest.approx(A1_OFFSET_X + 11 * WELL_SPACING)
        assert y == pytest.approx(A1_OFFSET_Y + 7 * WELL_SPACING)

    def test_spacing_between_adjacent_wells(self) -> None:
        x1, y1 = well_coordinates("A", 1)
        x2, y2 = well_coordinates("A", 2)
        assert x2 - x1 == pytest.approx(WELL_SPACING)
        assert y2 == pytest.approx(y1)

    def test_spacing_between_rows(self) -> None:
        x1, y1 = well_coordinates("A", 1)
        x2, y2 = well_coordinates("B", 1)
        assert x2 == pytest.approx(x1)
        assert y2 - y1 == pytest.approx(WELL_SPACING)


class TestGetWell:
    """Test WellPosition construction."""

    def test_well_name(self) -> None:
        well = get_well("A", 1)
        assert well.name == "A1"

    def test_well_coordinates_match(self) -> None:
        well = get_well("D", 6)
        x, y = well_coordinates("D", 6)
        assert well.x_mm == pytest.approx(x)
        assert well.y_mm == pytest.approx(y)

    def test_lowercase_row(self) -> None:
        well = get_well("a", 1)
        assert well.row == "A"


class TestAllWells:
    """Test full plate enumeration."""

    def test_count(self) -> None:
        wells = all_wells()
        assert len(wells) == 96

    def test_first_well(self) -> None:
        wells = all_wells()
        assert wells[0].name == "A1"

    def test_last_well(self) -> None:
        wells = all_wells()
        assert wells[-1].name == "H12"


class TestParseWellName:
    """Test well name parsing."""

    def test_simple(self) -> None:
        well = parse_well_name("A1")
        assert well.row == "A"
        assert well.col == 1

    def test_two_digit_column(self) -> None:
        well = parse_well_name("H12")
        assert well.row == "H"
        assert well.col == 12

    def test_lowercase(self) -> None:
        well = parse_well_name("b3")
        assert well.row == "B"
        assert well.col == 3

    def test_whitespace(self) -> None:
        well = parse_well_name("  C5 ")
        assert well.name == "C5"

    def test_invalid_row(self) -> None:
        with pytest.raises(ValueError):
            parse_well_name("Z1")

    def test_invalid_column(self) -> None:
        with pytest.raises(ValueError):
            parse_well_name("A13")

    def test_empty(self) -> None:
        with pytest.raises(ValueError):
            parse_well_name("")
