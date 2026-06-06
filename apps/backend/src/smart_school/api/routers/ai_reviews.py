from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.ai_review import schemas as ai_schemas
from smart_school.ai_review import services as ai_services
from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant

router = APIRouter(prefix="/ai/reports", tags=["AI Reports"])
ai_reports_read_permission = require_permission("ai_reports.read")
ai_reports_manage_permission = require_permission("ai_reports.manage")


@router.get("/queue", response_model=list[ai_schemas.AIReportRead])
async def list_ai_review_queue(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(ai_reports_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[ai_schemas.AIReportRead]:
    queue = await ai_services.list_queue(session, tenant.id)
    return [ai_schemas.AIReportRead.model_validate(report) for report in queue]


@router.get("/{report_id}", response_model=ai_schemas.AIReportRead)
async def read_ai_report(
    report_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(ai_reports_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> ai_schemas.AIReportRead:
    report = await ai_services.get_report(session, tenant.id, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI report not found.")
    return ai_schemas.AIReportRead.model_validate(report)


@router.get("/{report_id}/history", response_model=list[ai_schemas.AIReviewActionRead])
async def list_ai_review_history(
    report_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(ai_reports_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[ai_schemas.AIReviewActionRead]:
    history = await ai_services.list_history(session, tenant.id, report_id)
    return [ai_schemas.AIReviewActionRead.model_validate(action) for action in history]


@router.post("/{report_id}/review", response_model=ai_schemas.AIReportRead)
async def submit_ai_report_review(
    report_id: uuid.UUID,
    payload: ai_schemas.SubmitAIReviewRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    user: Annotated[User, Depends(ai_reports_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> ai_schemas.AIReportRead:
    try:
        report, _action = await ai_services.submit_review(
            session,
            tenant.id,
            report_id,
            user.id,
            payload.decision,
            payload.comment,
            payload.explainability,
            payload.metadata,
        )
        await session.commit()
        return ai_schemas.AIReportRead.model_validate(report)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
