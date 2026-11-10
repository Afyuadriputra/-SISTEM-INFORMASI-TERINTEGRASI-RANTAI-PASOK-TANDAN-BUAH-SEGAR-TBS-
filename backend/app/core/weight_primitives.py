"""Framework-free decimal weighing validation primitives (BR-008, BR-009, BIZ-004)."""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.core.exceptions import AppError, ErrorCode

_KG_PATTERN = re.compile(r"^-?\d{1,11}\.\d{3}$")


def parse_weighing_pair(gross_raw: str, tare_raw: str) -> tuple[Decimal, Decimal, Decimal]:
    """Validate gross/tare Decimal scales & bounds; compute authoritative net = gross - tare."""
    parsed: dict[str, Decimal] = {}
    for field_name, raw in (("gross_weight_kg", gross_raw), ("tare_weight_kg", tare_raw)):
        cleaned = raw.strip()
        if not _KG_PATTERN.match(cleaned):
            raise AppError(
                ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
                details=[
                    {
                        "field": field_name,
                        "reason": "Gunakan format berat desimal 3 angka di belakang koma (kg).",
                        "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                    }
                ],
            )
        try:
            val = Decimal(cleaned)
        except InvalidOperation as exc:
            raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
        if not val.is_finite() or val < Decimal("0"):
            raise AppError(ErrorCode.TBS_INVALID_WEIGHT)
        parsed[field_name] = val

    gross = parsed["gross_weight_kg"]
    tare = parsed["tare_weight_kg"]
    if gross <= Decimal("0"):
        raise AppError(
            ErrorCode.TBS_INVALID_WEIGHT,
            details=[
                {
                    "field": "gross_weight_kg",
                    "reason": "Berat bruto harus lebih besar dari nol.",
                    "code": ErrorCode.TBS_INVALID_WEIGHT.value,
                }
            ],
        )
    if tare > gross:
        raise AppError(
            ErrorCode.TBS_INVALID_WEIGHT,
            details=[
                {
                    "field": "tare_weight_kg",
                    "reason": f"Berat tara ({tare:.3f}) melebihi berat bruto ({gross:.3f}).",
                    "code": ErrorCode.TBS_INVALID_WEIGHT.value,
                }
            ],
        )
    net = (gross - tare).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    return gross, tare, net
