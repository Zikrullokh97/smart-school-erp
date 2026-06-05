from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, constr


class AIReviewActionRead(BaseModel):
    id: uuid.UUID
    ai_report_id: uuid.UUID
    actor_user_id: uuid.UUID | None
    decision: str
    comment: str | None
    explainability: dict[str, object]
    review_metadata: dict[str, object] = Field(alias="metadata")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIReportRead(BaseModel):
    id: uuid.UUID
    requested_by_user_id: uuid.UUID
    school_id: uuid.UUID | None
    report_type: str
    status: str
    prompt_hash: str
    input_parameters: dict[str, object]
    source_references: dict[str, object]
    output_summary: str | None
    reviewed_by_user_id: uuid.UUID | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmitAIReviewRequest(BaseModel):
    decision: constr(min_length=1, max_length=80)
    comment: str | None = None
    explainability: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)
