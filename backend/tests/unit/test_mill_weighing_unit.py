"""Unit tests for Evidence File validation, Mill Grading, and SM-06 ticket invariants (B7)."""

from __future__ import annotations

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.files.domain.rules import (
    MAX_UPLOAD_BYTES,
    detect_verified_mime,
    sanitize_filename,
)
from app.modules.mill_weighing.domain.entities import (
    MillGradingDeductionType,
    MillTicketStatus,
)
from app.modules.mill_weighing.domain.rules import (
    MillGradingInput,
    assert_ticket_can_revise,
    assert_ticket_can_verify,
    validate_mill_grading_items,
)


def test_detect_verified_mime_accepts_magic_signatures_and_blocks_spoofing() -> None:
    assert detect_verified_mime(b"%PDF-1.4\n%test", "application/pdf") == "application/pdf"
    assert detect_verified_mime(b"\xff\xd8\xff\xe0jpeg", "image/jpeg") == "image/jpeg"
    assert detect_verified_mime(b"\x89PNG\r\n\x1a\npng", "image/png") == "image/png"

    with pytest.raises(AppError) as exc_spoof:
        detect_verified_mime(b"<svg onload=alert(1)>", "image/png")
    assert exc_spoof.value.code == ErrorCode.VAL_INVALID_FORMAT

    with pytest.raises(AppError) as exc_empty:
        detect_verified_mime(b"", "application/pdf")
    assert exc_empty.value.code == ErrorCode.VAL_INVALID_FORMAT

    with pytest.raises(AppError) as exc_big:
        detect_verified_mime(b"%PDF-" + b"A" * MAX_UPLOAD_BYTES, "application/pdf")
    assert exc_big.value.code == ErrorCode.VAL_INVALID_FORMAT


def test_sanitize_filename_blocks_traversal() -> None:
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\win.ini") == "win.ini"
    assert sanitize_filename("slip timbang #9941.pdf") == "slip_timbang_9941.pdf"


def test_mill_grading_and_finality_guards() -> None:
    validated = validate_mill_grading_items(
        [
            MillGradingInput(
                grading_category="Sortasi PKS",
                deduction_type=MillGradingDeductionType.WEIGHT_PERCENT,
                deduction_value_raw="2.0000",
                calculation_basis="MILL_NET_WEIGHT",
                notes="Simulasi",
            )
        ]
    )
    assert len(validated) == 1

    with pytest.raises(AppError) as exc_rev:
        assert_ticket_can_revise(is_current=False, do_completed=False)
    assert exc_rev.value.code == ErrorCode.MILL_TICKET_ALREADY_FINAL

    with pytest.raises(AppError) as exc_ver:
        assert_ticket_can_verify(
            is_current=True, status=MillTicketStatus.VERIFIED, do_completed=False
        )
    assert exc_ver.value.code == ErrorCode.MILL_TICKET_ALREADY_FINAL
