from pathlib import Path
from sqlalchemy import inspect
from alembic import command
from alembic.config import Config
from saathi.db import Store


def test_empty_database_migration_restart_and_downgrade(tmp_path):
    url = f"sqlite:///{tmp_path / 'migration.sqlite3'}"
    store = Store(url)
    assert {
        "saathi_tasks",
        "saathi_approvals",
        "saathi_operations",
        "saathi_outbox",
    } <= set(inspect(store.engine).get_table_names())
    store.migrate()
    cfg = Config("alembic-saathi.ini")
    with store.engine.begin() as c:
        cfg.attributes["connection"] = c
        command.downgrade(cfg, "base")
    assert "saathi_tasks" not in inspect(store.engine).get_table_names()
    store.migrate()
    assert "saathi_tasks" in inspect(store.engine).get_table_names()
    store.engine.dispose()


def test_v1_upgrade_preserves_existing_booking_and_approval(tmp_path):
    import asyncio
    from datetime import datetime, timezone
    from saathi.config import Settings
    from saathi.runtime import Runtime
    from saathi.contracts import InboundMessage
    from sqlalchemy import select, func
    from saathi.db import schema

    url = f"sqlite:///{tmp_path / 'v1-upgrade.sqlite3'}"
    store = Store(url)
    runtime = Runtime(
        store, Settings(), clock=lambda: datetime(2026, 10, 28, tzinfo=timezone.utc)
    )
    user = runtime.create_user("en-IN")
    task = asyncio.run(
        runtime.handle(
            user, InboundMessage(external_id="old", text="Book Chennai 2026-10-31")
        )
    )
    preview = runtime.preview(
        user, task["id"], task["payload"]["slots"][0]["id"], task["version"]
    )
    approval = preview["payload"]["approval"]
    booked = runtime.decide(
        user, approval["id"], "approve", approval["token"], preview["version"]
    )
    cfg = Config("alembic-saathi.ini")
    with store.engine.begin() as connection:
        cfg.attributes["connection"] = connection
        command.downgrade(cfg, "0001")
    assert "saathi_media" not in inspect(store.engine).get_table_names()
    store.migrate()
    assert "saathi_media" in inspect(store.engine).get_table_names()
    assert (
        runtime.get(user, booked["id"])["payload"]["receipt"]
        == booked["payload"]["receipt"]
    )
    with store.engine.connect() as connection:
        assert (
            connection.scalar(select(func.count()).select_from(schema.approvals)) == 1
        )
        assert connection.scalar(select(func.count()).select_from(schema.outbox)) == 1
    store.engine.dispose()
