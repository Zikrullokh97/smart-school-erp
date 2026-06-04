from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Enum as SQLAlchemyEnum


def enum_type[EnumT: StrEnum](enum_class: type[EnumT], name: str) -> SQLAlchemyEnum:
    return SQLAlchemyEnum(
        enum_class,
        values_callable=lambda values: [item.value for item in values],
        name=name,
        native_enum=True,
        validate_strings=True,
    )
