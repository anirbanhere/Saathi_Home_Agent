import asyncio
from datetime import timedelta
import pytest
from test_runtime import prepare, approve, NOW, world
from saathi.outbox import drain_mock
from saathi.registry import ToolRegistry, MockAppointmentTool


def test_due_outbox_drain_is_idempotent_scoped_and_mock_only(world):
    runtime, user = world
    result = approve(runtime, user, prepare(runtime, user))
    assert drain_mock(runtime.store, user, now=NOW) == []
    other = runtime.create_user("en-IN")
    assert drain_mock(runtime.store, other, now=NOW + timedelta(days=10)) == []
    delivered = drain_mock(runtime.store, user, now=NOW + timedelta(days=10))
    assert len(delivered) == 1 and delivered[0]["mock"]
    assert drain_mock(runtime.store, user, now=NOW + timedelta(days=10)) == []


def test_registry_denies_unknown_tools_and_model_owned_approval(world):
    runtime, user = world
    registry = ToolRegistry()
    registry.register(MockAppointmentTool(runtime))
    with pytest.raises(ValueError):
        registry.register(MockAppointmentTool(runtime))
    with pytest.raises(ValueError):
        asyncio.run(
            registry.invoke(
                "payments.transfer", "execute", {}, {"human_approval": True}
            )
        )
    with pytest.raises(ValueError):
        asyncio.run(
            registry.invoke(
                "appointments.book",
                "execute",
                {},
                {"user_id": user, "human_approval": False},
            )
        )
