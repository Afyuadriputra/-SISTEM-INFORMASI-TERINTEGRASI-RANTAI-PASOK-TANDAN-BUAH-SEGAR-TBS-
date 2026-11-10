"""B0 baseline Alembic revision (empty chain anchor before B1-B10 incremental schemas).

Revision ID: 0001_b0_baseline
Revises:
Create Date: 2026-11-10
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0001_b0_baseline"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish baseline Alembic version tracking prior to B1 table migrations."""


def downgrade() -> None:
    """Revert B0 baseline revision."""
