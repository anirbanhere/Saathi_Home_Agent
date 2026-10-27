"""Explicit mock-only outbox drain. No scheduler, email, WhatsApp or network sends."""

from datetime import datetime, timezone
from sqlalchemy import select, update
from .db import schema as s


def drain_mock(store, user_id, *, now=None, limit=10):
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    if not 1 <= limit <= 10:
        raise ValueError("Drain budget must be1..10.")
    delivered = []
    with store.transaction(user_id) as c:
        rows = (
            c.execute(
                select(s.outbox)
                .where(
                    s.outbox.c.user_id == user_id,
                    s.outbox.c.status == "pending",
                    s.outbox.c.due_at <= stamp,
                )
                .order_by(s.outbox.c.due_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
            .mappings()
            .all()
        )
        for row in rows:
            if row["payload"].get("mock") is not True:
                raise ValueError("Live delivery is not enabled.")
            reference = "MOCK-DELIVERY-" + row["id"]
            c.execute(
                update(s.outbox)
                .where(s.outbox.c.id == row["id"])
                .values(status="mock_delivered", delivery_ref=reference)
            )
            delivered.append(
                {"reference": reference, "task_id": row["task_id"], "mock": True}
            )
    return delivered
