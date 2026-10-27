from enum import StrEnum
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

Locale = Literal["en-IN", "hi-IN", "ta-IN"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Profile(Contract):
    provider: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=120)
    timeout_seconds: int = Field(default=10, ge=1, le=120)
    retries: int = Field(default=0, ge=0, le=0)  # No implicit write/provider retries.


class InboundMessage(Contract):
    external_id: str = Field(min_length=1, max_length=100)
    channel: Literal["web_chat", "test_cli"] = "web_chat"
    conversation_id: str | None = Field(default=None, max_length=32)
    text: str = Field(default="", max_length=2000)
    locale: Locale = "en-IN"
    audio_base64: str | None = Field(default=None, max_length=45000)
    mime: Literal["audio/wav"] = "audio/wav"

    @model_validator(mode="after")
    def content_required(self):
        if bool(self.text.strip()) == bool(self.audio_base64):
            raise ValueError("Provide text or one bounded mock WAV fixture, not both.")
        return self


class Transcript(Contract):
    text: str = Field(min_length=1, max_length=4000)
    locale: Locale
    confidence: float | None = Field(default=None, ge=0, le=1)
    alternatives: list[str] = Field(default_factory=list, max_length=3)
    mock: bool = True


class AudioResult(Contract):
    audio_base64: str
    mime: str = "audio/wav"
    mock: bool = True


class ModelRequest(Contract):
    text: str = Field(max_length=6000)
    locale: Locale
    context: dict[str, Any] = Field(default_factory=dict)


class ModelResponse(Contract):
    text: str = Field(max_length=8000)
    mock: bool = True


class BookingIntent(Contract):
    service: Literal["dental_cleaning"] = "dental_cleaning"
    city: Literal["Chennai", "Bengaluru"] | None = None
    date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    preferred_window: Literal["morning"] = "morning"


class Action(StrEnum):
    READ = "READ"
    DRAFT = "DRAFT"
    OUTREACH = "OUTREACH"
    BOOK = "BOOK"
    ORDER = "ORDER"
    PAY = "PAY"
    DELETE = "DELETE"
    SHARE = "SHARE"


class Step(Contract):
    tool: Literal[
        "appointments.search",
        "appointments.prepare",
        "appointments.book",
        "reminders.draft",
    ]
    action: Action
    requires_approval: bool
    timeout_seconds: int = Field(default=10, ge=1, le=30)
    prerequisite: str | None = None
    expected_output: str
    compensation: str = (
        "Pre-commit cancellation only; committed bookings require a separate cancellation operation."
    )


class TaskPlan(Contract):
    goal: str
    steps: list[Step] = Field(min_length=1, max_length=8)


class ToolManifest(Contract):
    name: str
    action: Action
    provider: str = "mock_clinic"
    permission: str = "mock_dental"
    mock: bool = True
    idempotent: bool = True
    input_schema: dict
    output_schema: dict


class OutboundMessage(Contract):
    task_id: str
    text: str
    locale: Locale
    mock: bool = True


class DeliveryReceipt(Contract):
    reference: str
    status: Literal["mock_delivered", "pending"]
    mock: bool = True


class ChannelAdapter(Protocol):
    async def normalize_inbound(self, payload: dict) -> InboundMessage: ...
    async def send_message(self, message: OutboundMessage) -> DeliveryReceipt: ...
    async def send_approval(self, message: OutboundMessage) -> DeliveryReceipt: ...


class LLMProvider(Protocol):
    async def generate(self, request: ModelRequest) -> ModelResponse: ...
    async def structured_generate(
        self, request: ModelRequest, schema: type[Contract]
    ) -> Contract: ...


class SpeechToTextProvider(Protocol):
    async def transcribe(
        self, audio: bytes, mime: str, language_hint: str | None
    ) -> Transcript: ...


class TextToSpeechProvider(Protocol):
    async def synthesize(
        self, text: str, language: str, voice: str | None = None
    ) -> AudioResult: ...


class ToolAdapter(Protocol):
    def manifest(self) -> ToolManifest: ...
    async def prepare(self, args: dict, context: dict) -> dict: ...
    async def execute(self, args: dict, context: dict) -> dict: ...
    async def reconcile(self, external_id: str, context: dict) -> dict: ...


class AgentRuntime(Protocol):
    async def handle(self, user_id: str, message: InboundMessage) -> dict: ...
    async def resume(self, user_id: str, task_id: str, event: dict) -> dict: ...
