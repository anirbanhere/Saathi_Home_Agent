"""Allowlisted typed native-tool boundary; no remote MCP transport is enabled."""

from .contracts import Contract, ToolManifest, Action
from .policy import Policy
from pydantic import Field


class AppointmentArgs(Contract):
    task_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    version: int = Field(ge=0, strict=True)
    slot_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")
    approval_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")


class MockAppointmentTool:
    def __init__(self, runtime):
        self.runtime = runtime

    def manifest(self):
        return ToolManifest(
            name="appointments.book",
            action=Action.BOOK,
            input_schema=AppointmentArgs.model_json_schema(),
            output_schema={"type": "object", "required": ["id", "status", "payload"]},
        )

    async def prepare(self, args, context):
        parsed = AppointmentArgs.model_validate(args)
        if not parsed.slot_id:
            raise ValueError("Choose an observed mock slot.")
        return self.runtime.preview(
            context["user_id"], parsed.task_id, parsed.slot_id, parsed.version
        )

    async def execute(self, args, context):
        parsed = AppointmentArgs.model_validate(args)
        if not parsed.approval_id:
            raise ValueError("Server approval reference is required.")
        return self.runtime.decide(
            context["user_id"],
            parsed.approval_id,
            "approve",
            context["approval_token"],
            parsed.version,
        )

    async def reconcile(self, external_id, context):
        # Here the lookup is a scoped task reference, never a new execute request.
        return self.runtime.reconcile(
            context["user_id"], external_id, context["version"]
        )


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        manifest = ToolManifest.model_validate(tool.manifest())
        if manifest.name in self.tools or not manifest.mock:
            raise ValueError("Duplicate or live tool registration is not allowed.")
        Policy().check(
            manifest.name, manifest.action, mock=manifest.mock, approved=True
        )
        self.tools[manifest.name] = tool

    def manifest(self):
        return [tool.manifest().model_dump(mode="json") for tool in self.tools.values()]

    async def invoke(self, name, phase, args, context):
        if name not in self.tools or phase not in {"prepare", "execute", "reconcile"}:
            raise ValueError("Tool or execution phase is not allowlisted.")
        tool = self.tools[name]
        manifest = tool.manifest()
        if phase == "execute":
            Policy().check(
                name,
                manifest.action,
                mock=manifest.mock,
                approved=context.get("human_approval") is True,
            )
        result = await getattr(tool, phase)(args, context)
        if (
            not isinstance(result, dict)
            or result.get("payload", {}).get("mock") is not True
        ):
            raise ValueError("Tool did not return a labeled mock task.")
        return result
