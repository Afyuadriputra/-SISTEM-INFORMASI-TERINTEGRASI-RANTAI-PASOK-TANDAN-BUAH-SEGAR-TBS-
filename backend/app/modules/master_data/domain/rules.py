"""Pure business validation rules for Master Data (Decimal precision, coordinates, codes)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from app.core.exceptions import AppError, ErrorCode

_AREA_PATTERN = re.compile(r"^\d{1,8}\.\d{4}$")
_KG_PATTERN = re.compile(r"^\d{1,11}\.\d{3}$")
_COORD_PATTERN = re.compile(r"^-?\d{1,3}(?:\.\d{1,6})?$")


def parse_positive_decimal(
    raw: str,
    *,
    pattern: re.Pattern[str],
    field_name: str,
    precision_hint: str,
) -> Decimal:
    """Strictly parse positive Decimal string matching exact OpenAPI precision pattern."""
    stripped = raw.strip()
    if not pattern.match(stripped):
        raise AppError(
            ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
            f"Nilai {field_name} tidak valid. Gunakan format desimal ({precision_hint}).",
            details=[
                {
                    "field": field_name,
                    "reason": f"Format harus sesuai {precision_hint}.",
                    "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                }
            ],
        )
    try:
        value = Decimal(stripped)
    except InvalidOperation as exc:
        raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
    if not value.is_finite() or value <= Decimal("0"):
        raise AppError(
            ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
            f"Nilai {field_name} harus lebih besar dari nol.",
            details=[
                {
                    "field": field_name,
                    "reason": "Harus bernilai positif (> 0).",
                    "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                }
            ],
        )
    return value


def parse_area_hectares(raw: str) -> Decimal:
    """Validate and parse NUMERIC(12,4) positive farm area in hectares."""
    return parse_positive_decimal(
        raw,
        pattern=_AREA_PATTERN,
        field_name="area_hectares",
        precision_hint="4 angka di belakang koma, mis. 2.5000",
    )


def parse_nominal_capacity_kg(raw: str | None) -> Decimal | None:
    """Validate and parse optional NUMERIC(14,3) positive nominal capacity in kg."""
    if raw is None:
        return None
    return parse_positive_decimal(
        raw,
        pattern=_KG_PATTERN,
        field_name="nominal_capacity_kg",
        precision_hint="3 angka di belakang koma, mis. 12000.000",
    )


def parse_coordinate_pair(
    latitude_raw: str | None,
    longitude_raw: str | None,
) -> tuple[Decimal | None, Decimal | None]:
    """Validate paired WGS84 coordinates (BR-MD-014, VAL_INVALID_COORDINATES)."""
    lat_clean = latitude_raw.strip() if isinstance(latitude_raw, str) else None
    lng_clean = longitude_raw.strip() if isinstance(longitude_raw, str) else None
    if not lat_clean:
        lat_clean = None
    if not lng_clean:
        lng_clean = None

    if lat_clean is None and lng_clean is None:
        return None, None
    if lat_clean is None or lng_clean is None:
        raise AppError(
            ErrorCode.VAL_INVALID_COORDINATES,
            details=[
                {
                    "field": "latitude" if lat_clean is None else "longitude",
                    "reason": (
                        "Latitude dan Longitude harus diisi berpasangan atau dikosongkan keduanya."
                    ),
                    "code": ErrorCode.VAL_INVALID_COORDINATES.value,
                }
            ],
        )

    if not _COORD_PATTERN.match(lat_clean) or not _COORD_PATTERN.match(lng_clean):
        raise AppError(ErrorCode.VAL_INVALID_COORDINATES)
    try:
        lat = Decimal(lat_clean).quantize(Decimal("0.000001"))
        lng = Decimal(lng_clean).quantize(Decimal("0.000001"))
    except InvalidOperation as exc:
        raise AppError(ErrorCode.VAL_INVALID_COORDINATES) from exc

    if not lat.is_finite() or lat < Decimal("-90") or lat > Decimal("90"):
        raise AppError(ErrorCode.VAL_INVALID_COORDINATES)
    if not lng.is_finite() or lng < Decimal("-180") or lng > Decimal("180"):
        raise AppError(ErrorCode.VAL_INVALID_COORDINATES)
    return lat, lng


def normalize_plate_number(raw: str) -> str:
    """Normalize Indonesian vehicle plate spacing and case cleanly."""
    normalized = " ".join(raw.strip().upper().split())
    if len(normalized) < 3 or len(normalized) > 25:
        raise AppError(ErrorCode.VAL_INVALID_FORMAT, "Nomor polisi tidak valid (3-25 karakter).")
    return normalized
