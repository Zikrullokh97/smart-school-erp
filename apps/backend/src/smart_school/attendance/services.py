from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.attendance import crud as attendance_crud
from smart_school.models.attendance import (
    AttendanceEvent,
    AttendanceMethod,
    AttendanceSource,
    FaceEmbedding,
)


@dataclass(frozen=True)
class AttendanceCaptureResult:
    method: AttendanceMethod
    source: AttendanceSource
    fraud_score: Decimal | None
    fraud_flags: dict[str, object]
    evidence: dict[str, object]


async def _has_face_embedding_for_student(
    session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID
) -> bool:
    result = await session.execute(
        select(FaceEmbedding).filter_by(tenant_id=tenant_id, student_id=student_id)
    )
    return result.scalar_one_or_none() is not None


def _build_fraud_context(
    method: AttendanceMethod,
    face_token_present: bool,
    qr_code_present: bool,
    nfc_present: bool,
    manual_confirmation: bool,
    face_matched: bool,
) -> tuple[Decimal | None, dict[str, object]]:
    fraud_flags: dict[str, object] = {}
    fraud_score: Decimal | None = None

    if manual_confirmation and (face_token_present or qr_code_present or nfc_present):
        fraud_flags["manual_fallback"] = True
        fraud_score = Decimal("0.60")
    if method == AttendanceMethod.MANUAL and face_token_present and not face_matched:
        fraud_flags["face_id_fallback"] = "failed_to_match"
        fraud_score = Decimal("0.75")
    if method == AttendanceMethod.QR_CODE and face_token_present and not face_matched:
        fraud_flags["face_id_skipped"] = True
        fraud_score = Decimal("0.20")

    return fraud_score, fraud_flags


async def determine_attendance_capture(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
    face_id_token: str | None = None,
    qr_code_token: str | None = None,
    nfc_tag: str | None = None,
    manual_confirmation: bool | None = None,
    source: str = "manual",
) -> AttendanceCaptureResult:
    face_token_present = bool(face_id_token)
    qr_code_present = bool(qr_code_token)
    nfc_present = bool(nfc_tag)
    face_matched = False

    if face_token_present:
        face_matched = await _has_face_embedding_for_student(session, tenant_id, student_id)
        if face_matched:
            method = AttendanceMethod.FACE_ID
            chosen_source = AttendanceSource.FACE_ID
        else:
            method = None
    else:
        method = None

    if method is None and qr_code_present:
        method = AttendanceMethod.QR_CODE
        chosen_source = AttendanceSource.QR_CODE

    if method is None and nfc_present:
        method = AttendanceMethod.NFC
        chosen_source = AttendanceSource.NFC

    if method is None and manual_confirmation:
        method = AttendanceMethod.MANUAL
        chosen_source = AttendanceSource.MANUAL

    if method is None:
        raise ValueError("No valid attendance capture method provided.")

    fraud_score, fraud_flags = _build_fraud_context(
        method,
        face_token_present,
        qr_code_present,
        nfc_present,
        bool(manual_confirmation),
        face_matched,
    )

    evidence: dict[str, object] = {
        "fallback_path": [
            method.value,
        ],
        "requested_source": source,
    }
    if face_token_present:
        evidence["face_id_token_present"] = True
    if qr_code_present:
        evidence["qr_code_token_present"] = True
    if nfc_present:
        evidence["nfc_tag_present"] = True
    if manual_confirmation:
        evidence["manual_confirmation"] = True

    return AttendanceCaptureResult(
        method=method,
        source=chosen_source,
        fraud_score=fraud_score,
        fraud_flags=fraud_flags,
        evidence=evidence,
    )


async def capture_attendance_event(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    session_id: uuid.UUID,
    student_id: uuid.UUID,
    event_type: str,
    face_id_token: str | None,
    qr_code_token: str | None,
    nfc_tag: str | None,
    manual_confirmation: bool | None,
    source: str,
    captured_at: object,
    captured_by_user_id: uuid.UUID | None,
    idempotency_key: str,
    confidence_score: float | None,
    notes: str | None,
) -> tuple[AttendanceEvent, AttendanceCaptureResult]:
    capture_result = await determine_attendance_capture(
        session,
        tenant_id,
        student_id,
        face_id_token=face_id_token,
        qr_code_token=qr_code_token,
        nfc_tag=nfc_tag,
        manual_confirmation=manual_confirmation,
        source=source,
    )

    attendance_event = await attendance_crud.create_event(
        session,
        tenant_id,
        session_id,
        student_id,
        event_type,
        capture_result.source.value,
        capture_result.method.value,
        captured_at,
        captured_by_user_id,
        idempotency_key,
        fraud_score=float(capture_result.fraud_score)
        if capture_result.fraud_score is not None
        else None,
        fraud_flags=capture_result.fraud_flags,
        confidence_score=confidence_score,
        evidence={**capture_result.evidence, **({} if notes is None else {"notes": notes})},
        notes=notes,
    )
    return attendance_event, capture_result
