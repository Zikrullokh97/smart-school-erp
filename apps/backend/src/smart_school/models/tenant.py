from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smart_school.db.base import Base
from smart_school.models.common import enum_type
from smart_school.models.enums import TenantStatus
from smart_school.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from smart_school.models.school import School


class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TenantStatus] = mapped_column(
        enum_type(TenantStatus, "tenant_status"),
        nullable=False,
        default=TenantStatus.ACTIVE,
        server_default=TenantStatus.ACTIVE.value,
    )
    locale: Mapped[str] = mapped_column(String(16), nullable=False, default="ky-KG")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Bishkek")

    schools: Mapped[list[School]] = relationship(back_populates="tenant")
