"""Frozen version-one schema; future changes belong in new migrations."""

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    Integer,
    JSON,
    UniqueConstraint,
    ForeignKey,
)

metadata = MetaData()

users = Table(
    "saathi_users",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("locale", String(8), nullable=False),
    Column("created_at", String(40), nullable=False),
)
sessions = Table(
    "saathi_sessions",
    metadata,
    Column("token_hash", String(64), primary_key=True),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("expires_at", String(40), nullable=False),
    Column("csrf", String(64), nullable=False),
)
conversations = Table(
    "saathi_conversations",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("channel", String(20), nullable=False),
)
tasks = Table(
    "saathi_tasks",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("conversation_id", ForeignKey(conversations.c.id), nullable=False),
    Column("status", String(40), nullable=False),
    Column("version", Integer, nullable=False),
    Column("locale", String(8), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("profiles", JSON, nullable=False),
    Column("updated_at", String(40), nullable=False),
)
messages = Table(
    "saathi_messages",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("conversation_id", ForeignKey(conversations.c.id), nullable=False),
    Column("channel", String(20), nullable=False),
    Column("external_id", String(100), nullable=False),
    Column("fingerprint", String(64), nullable=False),
    Column("response", JSON, nullable=False),
    UniqueConstraint("user_id", "channel", "external_id"),
)
approvals = Table(
    "saathi_approvals",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("task_id", ForeignKey(tasks.c.id), nullable=False),
    Column("version", Integer, nullable=False),
    Column("preview_hash", String(64), nullable=False),
    Column("token_hash", String(64), nullable=False),
    Column("expires_at", String(40), nullable=False),
    Column("decision", String(20), nullable=True),
)
slots = Table(
    "saathi_mock_slots",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("city", String(40), nullable=False),
    Column("starts_at", String(40), nullable=False),
    Column("revision", Integer, nullable=False),
    Column("booked_task", ForeignKey(tasks.c.id), unique=True, nullable=True),
)
operations = Table(
    "saathi_operations",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("task_id", ForeignKey(tasks.c.id), nullable=False, unique=True),
    Column("status", String(40), nullable=False),
    Column("reference", String(80), nullable=False, unique=True),
    Column("receipt", JSON, nullable=False),
)
outbox = Table(
    "saathi_outbox",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("task_id", ForeignKey(tasks.c.id), nullable=False),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("dedupe_key", String(100), nullable=False, unique=True),
    Column("event", String(50), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("due_at", String(40), nullable=False),
    Column("status", String(30), nullable=False),
    Column("delivery_ref", String(80), nullable=True),
)
audit = Table(
    "saathi_audit",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", ForeignKey(users.c.id), nullable=False),
    Column("task_id", ForeignKey(tasks.c.id), nullable=True),
    Column("event", String(60), nullable=False),
    Column("at", String(40), nullable=False),
)
