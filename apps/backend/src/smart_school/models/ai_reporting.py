from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from smart_school.db.base import Base
from smart_school.models.common import enum_type
from smart_school.models.enums import AIReportStatus
from smart_school.models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AIReport(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "ai_reports"

    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    school_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[AIReportStatus] = mapped_column(
        enum_type(AIReportStatus, "ai_report_status"),
        nullable=False,
        default=AIReportStatus.REQUESTED,
        server_default=AIReportStatus.REQUESTED.value,
    )
    prompt_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    input_parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    source_references: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output_summary: Mapped[str | None] = mapped_column(String(8000), nullable=True)
    output_embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
