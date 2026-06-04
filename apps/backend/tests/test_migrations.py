from __future__ import annotations

import importlib.util
from pathlib import Path


def test_initial_migration_revision_metadata() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "20260604_0001_initial_schema.py"
    )
    spec = importlib.util.spec_from_file_location("initial_schema", migration_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "20260604_0001"
    assert module.down_revision is None
    assert callable(module.upgrade)
    assert callable(module.downgrade)


def test_alembic_configuration_exists() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    assert (backend_root / "alembic.ini").is_file()
    assert (backend_root / "migrations" / "env.py").is_file()
    assert (backend_root / "migrations" / "script.py.mako").is_file()
