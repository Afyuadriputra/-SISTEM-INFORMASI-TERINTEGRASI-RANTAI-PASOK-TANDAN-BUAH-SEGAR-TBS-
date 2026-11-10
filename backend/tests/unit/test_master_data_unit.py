"""Unit tests for Master Data domain rules (coordinates, Decimal scales, plates)."""

from __future__ import annotations

from decimal import Decimal

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.master_data.domain.rules import (
    normalize_plate_number,
    parse_area_hectares,
    parse_coordinate_pair,
    parse_nominal_capacity_kg,
)


def test_parse_coordinate_pair_valid_and_unpaired_or_out_of_range() -> None:
    lat, lng = parse_coordinate_pair("0.402100", "101.860400")
    assert lat == Decimal("0.402100")
    assert lng == Decimal("101.860400")
    assert parse_coordinate_pair(None, None) == (None, None)

    for bad_lat, bad_lng in [
        ("0.402100", None),
        (None, "101.860400"),
        ("-90.000001", "101.860400"),
        ("91.000000", "101.860400"),
        ("0.402100", "180.000001"),
        ("0.4021001", "101.860400"),
    ]:
        with pytest.raises(AppError) as exc:
            parse_coordinate_pair(bad_lat, bad_lng)
        assert exc.value.code == ErrorCode.VAL_INVALID_COORDINATES
        assert exc.value.status_code == 422


def test_decimal_precision_guards_for_area_and_capacity() -> None:
    assert parse_area_hectares("2.5000") == Decimal("2.5000")
    for invalid_area in ("0.0000", "-1.0000", "2.50", "2.50000", "abc"):
        with pytest.raises(AppError) as exc:
            parse_area_hectares(invalid_area)
        assert exc.value.code == ErrorCode.VAL_INVALID_DECIMAL_PRECISION
        assert exc.value.status_code == 422

    assert parse_nominal_capacity_kg("12000.000") == Decimal("12000.000")
    assert parse_nominal_capacity_kg(None) is None
    for invalid_cap in ("0.000", "12000", "12000.00"):
        with pytest.raises(AppError) as exc:
            parse_nominal_capacity_kg(invalid_cap)
        assert exc.value.code == ErrorCode.VAL_INVALID_DECIMAL_PRECISION


def test_normalize_plate_number() -> None:
    assert normalize_plate_number("  bm   9042  ts ") == "BM 9042 TS"
    with pytest.raises(AppError) as exc:
        normalize_plate_number("A")
    assert exc.value.code == ErrorCode.VAL_INVALID_FORMAT
