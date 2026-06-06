from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.ai_review import crud as ai_review_crud
from smart_school.models.enums import AIReviewDecision


async def get_report(session: AsyncSession, tenant_id: uuid.UUID, report_id: uuid.UUID):
    return await ai_review_crud.get_report_by_id(session, tenant_id, report_id)


async def list_queue(session: AsyncSession, tenant_id: uuid.UUID):
    return await ai_review_crud.list_review_queue(session, tenant_id)


async def list_history(session: AsyncSession, tenant_id: uuid.UUID, report_id: uuid.UUID):
    return await ai_review_crud.list_review_history(session, tenant_id, report_id)


async def submit_review(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    report_id: uuid.UUID,
    actor_user_id: uuid.UUID | None,
    decision: str,
    comment: str | None,
    explainability: dict[str, object],
    metadata: dict[str, object],
):
    report = await ai_review_crud.get_report_by_id(session, tenant_id, report_id)
    if report is None:
        raise ValueError("AI report not found.")

    try:
        decision_enum = AIReviewDecision(decision)
    except ValueError as exc:
        raise ValueError("Invalid review decision.") from exc

    action = await ai_review_crud.create_review_action(
        session,
        tenant_id,
        report_id,
        actor_user_id,
        decision_enum,
        comment,
        explainability,
        metadata,
    )
    await ai_review_crud.mark_report_reviewed(session, report, actor_user_id)
    return report, action
