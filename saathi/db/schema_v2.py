"""Frozen version-two metadata: v1 plus private local media, without mutating v1."""

from sqlalchemy import MetaData, Table, Column, String, Integer, ForeignKey
from . import schema_v1

metadata = MetaData()
for table in schema_v1.metadata.sorted_tables:
    table.to_metadata(metadata)

media = Table(
    "saathi_media",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", ForeignKey("saathi_users.id"), nullable=False, index=True),
    Column("state", String(16), nullable=False),
    Column("sha256", String(64), nullable=True),
    Column("bytes", Integer, nullable=True),
    Column("duration_ms", Integer, nullable=True),
    Column("created_at", String(40), nullable=False),
    Column("expires_at", String(40), nullable=False),
    Column("consent", String(30), nullable=False),
)
