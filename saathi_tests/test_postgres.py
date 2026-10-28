"""Real PostgreSQL/Redis check: optional locally, mandatory in Saathi CI."""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema
from saathi.config import Settings
from saathi.contracts import InboundMessage
from saathi.db import Store, schema
from saathi.runtime import Runtime
from test_runtime import approve


def test_real_postgres_migration_concurrency_restart_and_redis_readiness(tmp_path):
    url = os.environ.get("SAATHI_TEST_POSTGRES_URL")
    if not url:
        pytest.skip(
            "Real PostgreSQL/Redis are exercised in CI; local Docker daemon unavailable."
        )
    parsed = make_url(url)
    assert (
        parsed.host in {"127.0.0.1", "localhost"} and parsed.database == "saathi_test"
    )
    namespace = "saathi_ci_" + uuid4().hex
    admin = create_engine(url)
    store = restarted = None
    with admin.begin() as c:
        c.execute(CreateSchema(namespace))
    try:
        scoped = parsed.update_query_dict(
            {"options": "-csearch_path=" + namespace}
        ).render_as_string(hide_password=False)
        store = Store(scoped)
        runtime = Runtime(
            store,
            Settings(),
            clock=lambda: datetime(2026, 10, 27, 5, tzinfo=timezone.utc),
        )
        users = [runtime.create_user("en-IN") for _ in range(2)]
        from saathi.media import MediaStore
        from saathi.speech import fixture_audio

        local_media = MediaStore(store, Settings(media_root=str(tmp_path / "pg-media")))
        audio = local_media.upload(
            users[0], fixture_audio("en-IN"), "audio/wav", consent=True
        )
        assert local_media.content(users[0], audio["id"]) == fixture_audio("en-IN")
        assert local_media.delete(users[0], audio["id"])["state"] == "deleted"
        previews = []
        for user in users:
            task = asyncio.run(
                runtime.handle(
                    user,
                    InboundMessage(
                        external_id=uuid4().hex, text="Book Chennai 2026-10-31"
                    ),
                )
            )
            previews.append(
                runtime.preview(
                    user, task["id"], task["payload"]["slots"][0]["id"], task["version"]
                )
            )
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(approve, runtime, user, task)
                for user, task in zip(users, previews)
            ]
            results = [f.result() for f in futures]
        assert sorted(r["status"] for r in results) == [
            "COMPLETED",
            "REQUIRES_USER_ACTION",
        ]
        completed = next(r for r in results if r["status"] == "COMPLETED")
        restarted = Runtime(Store(scoped), Settings())
        assert restarted.get(completed["user_id"], completed["id"])["payload"][
            "receipt"
        ]["verified"]
        with store.engine.connect() as c:
            assert c.scalar(select(func.count()).select_from(schema.operations)) == 1
        import redis

        assert redis.Redis.from_url(
            os.environ["SAATHI_TEST_REDIS_URL"], socket_timeout=3
        ).ping()
    finally:
        if restarted:
            restarted.store.engine.dispose()
        if store:
            store.engine.dispose()
        # Only the server-generated schema in a verified loopback test DB is removed.
        assert namespace.startswith("saathi_ci_") and len(namespace) == 42
        with admin.begin() as c:
            c.execute(DropSchema(namespace, cascade=True))
        admin.dispose()
