from __future__ import annotations

import uuid
from sqlalchemy import ForeignKey, String, Uuid, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from smart_school.db.base import Base
from smart_school.models.common import enum_type
from smart_school.models.enums import AIReviewDecision
from smart_school.models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AIReviewAction(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "ai_review_actions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "ai_report_id", "actor_user_id", "created_at", name="uq_ai_review_actions"),
    )

    ai_report_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    decision: Mapped[AIReviewDecision] = mapped_column(
        enum_type(AIReviewDecision, "ai_review_decision"),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    explainability: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    review_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
