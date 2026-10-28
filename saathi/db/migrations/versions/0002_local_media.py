"""Add only the private local media table; preserve existing tasks and consent."""

from alembic import op
from saathi.db.schema_v2 import media

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    media.create(op.get_bind(), checkfirst=False)


def downgrade():
    media.drop(op.get_bind(), checkfirst=False)
