from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.ai_reporting import AIReport
from smart_school.models.ai_review import AIReviewAction
from smart_school.models.enums import AIReviewDecision, AIReportStatus


async def get_report_by_id(session: AsyncSession, tenant_id: uuid.UUID, report_id: uuid.UUID) -> AIReport | None:
    result = await session.execute(select(AIReport).filter_by(tenant_id=tenant_id, id=report_id))
    return result.scalar_one_or_none()


async def list_review_queue(session: AsyncSession, tenant_id: uuid.UUID) -> list[AIReport]:
    result = await session.execute(
        select(AIReport)
        .filter(AIReport.tenant_id == tenant_id)
        .filter(AIReport.status.in_([AIReportStatus.REQUESTED, AIReportStatus.PROCESSING]))
        .order_by(AIReport.created_at.asc())
    )
    return result.scalars().all()


async def list_review_history(session: AsyncSession, tenant_id: uuid.UUID, report_id: uuid.UUID) -> list[AIReviewAction]:
    result = await session.execute(
        select(AIReviewAction)
        .filter_by(tenant_id=tenant_id, ai_report_id=report_id)
        .order_by(AIReviewAction.created_at.asc())
    )
    return result.scalars().all()


async def create_review_action(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    report_id: uuid.UUID,
    actor_user_id: uuid.UUID | None,
    decision: AIReviewDecision,
    comment: str | None,
    explainability: dict[str, object],
    metadata: dict[str, object],
) -> AIReviewAction:
    action = AIReviewAction(
        tenant_id=tenant_id,
        ai_report_id=report_id,
        actor_user_id=actor_user_id,
        decision=decision,
        comment=comment,
        explainability=explainability,
        review_metadata=metadata,
    )
    session.add(action)
    await session.flush()
    return action


async def mark_report_reviewed(
    session: AsyncSession,
    report: AIReport,
    reviewed_by_user_id: uuid.UUID | None,
) -> AIReport:
    report.status = AIReportStatus.REVIEWED
    report.reviewed_by_user_id = reviewed_by_user_id
    report.reviewed_at = datetime.now()
    await session.flush()
    return report
