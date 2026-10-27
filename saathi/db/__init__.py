from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine, event, select
from alembic.config import Config
from alembic import command
from . import schema_v1 as schema


class Store:
    def __init__(self, url):
        self.url = url
        if url.startswith("sqlite:///") and not url.endswith(":memory:"):
            Path(url[len("sqlite:///") :]).parent.mkdir(parents=True, exist_ok=True)
        kwargs = (
            {"connect_args": {"check_same_thread": False, "timeout": 15}}
            if url.startswith("sqlite:")
            else {"pool_pre_ping": True}
        )
        self.engine = create_engine(url, **kwargs)
        if self.engine.dialect.name == "sqlite":

            @event.listens_for(self.engine, "connect")
            def foreign_keys(connection, record):
                connection.execute("PRAGMA foreign_keys=ON")

        self.migrate()

    def migrate(self):
        cfg = Config(str(Path(__file__).resolve().parents[2] / "alembic-saathi.ini"))
        cfg.set_main_option(
            "script_location", str(Path(__file__).parent / "migrations")
        )
        with self.engine.begin() as connection:
            cfg.attributes["connection"] = connection
            command.upgrade(cfg, "head")

    @contextmanager
    def transaction(self, user_id=None):
        with self.engine.connect() as connection:
            try:
                if self.engine.dialect.name == "sqlite":
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
                else:
                    connection.begin()
                    if user_id:
                        connection.execute(
                            select(schema.users.c.id)
                            .where(schema.users.c.id == user_id)
                            .with_for_update()
                        )
                yield connection
                connection.commit()
            except BaseException:
                connection.rollback()
                raise
