import os
from alembic import context
from sqlalchemy import create_engine
from saathi.db.schema_v1 import metadata

config = context.config
connection = config.attributes.get("connection")

if context.is_offline_mode():
    context.configure(
        url=os.environ.get(
            "SAATHI_DATABASE_URL", config.get_main_option("sqlalchemy.url")
        ),
        target_metadata=metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
elif connection is not None:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(
        os.environ.get("SAATHI_DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    )
    with engine.begin() as connection:
        context.configure(connection=connection, target_metadata=metadata)
        with context.begin_transaction():
            context.run_migrations()
