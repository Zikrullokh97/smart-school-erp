from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, constr


class GamificationProfileRead(BaseModel):
    student_id: uuid.UUID
    xp_total: int
    level: int
    streak_count: int
    streak_start_date: datetime | None = None
    last_activity_at: datetime | None = None
    badges: list[dict[str, object]] = Field(default_factory=list)
    active_challenges: list[dict[str, object]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AwardXPRequest(BaseModel):
    amount: int = Field(gt=0)
    activity_type: constr(min_length=1, max_length=120)
    source: constr(min_length=1, max_length=120)
    note: str | None = None


class LeaderboardEntryRead(BaseModel):
    student_id: uuid.UUID
    student_number: str
    first_name: str
    last_name: str
    xp_total: int
    level: int

    model_config = ConfigDict(from_attributes=True)


class ChallengeCompleteRequest(BaseModel):
    evidence: dict[str, object] = Field(default_factory=dict)
    comment: str | None = None


class BadgeRead(BaseModel):
    code: str
    name: str
    description: str | None
    icon: str | None
    xp_threshold: int
    metadata: dict[str, object]

    model_config = ConfigDict(from_attributes=True)


class StudentChallengeRead(BaseModel):
    challenge_id: uuid.UUID
    code: str
    name: str
    description: str | None
    xp_reward: int
    goal_count: int
    status: str
    progress_count: int
    completed_at: datetime | None
    metadata: dict[str, object]

    model_config = ConfigDict(from_attributes=True)
