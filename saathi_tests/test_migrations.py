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
