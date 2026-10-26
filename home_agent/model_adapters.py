"""Small provider-neutral completion contract; domain permissions stay in the app."""

from copy import deepcopy
from dataclasses import dataclass
import math
import time
from typing import Protocol
from urllib.parse import urlsplit

from .errors import AppError, text


def free_model(model):
    if not isinstance(model, str) or not (
        model == "openrouter/free" or model.endswith(":free")
    ):
        raise AppError(
            "Only OpenRouter free models are enabled.", 422, "PAID_MODEL_DISABLED"
        )
    if len(model) > 160 or any(c.isspace() for c in model):
        raise AppError("Invalid model identifier.")
    return model


@dataclass(frozen=True)
class ModelProfile:
    provider: str
    model: str


@dataclass(frozen=True)
class CompletionRequest:
    messages: list[dict]
    tools: list[dict]
    tool_choice: str = "auto"
    max_tokens: int = 1400

    def __post_init__(self):
        if (
            not isinstance(self.messages, list)
            or not self.messages
            or not all(isinstance(m, dict) for m in self.messages)
        ):
            raise AppError("Completion messages must be a nonempty list of objects.")
        if not isinstance(self.tools, list) or not all(
            isinstance(tool, dict) for tool in self.tools
        ):
            raise AppError("Completion tools must be a list of schemas.")
        if not isinstance(self.tool_choice, str) or self.tool_choice not in {
            "auto",
            "none",
        }:
            raise AppError("Unsupported completion tool choice.")
        if (
            isinstance(self.max_tokens, bool)
            or not isinstance(self.max_tokens, int)
            or not 1 <= self.max_tokens <= 4096
        ):
            raise AppError("Completion token budget must be between 1 and 4096.")


@dataclass(frozen=True)
class CompletionResult:
    message: dict
    model: str
    usage: dict
    elapsed_ms: int


class CompletionAdapter(Protocol):
    profile: ModelProfile

    def complete(self, request: CompletionRequest) -> CompletionResult: ...


def provider_error(status):
    """Never surface raw provider messages, metadata, prompts or credentials."""
    errors = {
        401: (
            "The inference service rejected its server credential. Direct tools remain available.",
            503,
            "MODEL_AUTH_ERROR",
        ),
        402: (
            "The provider rejected this request under its account usage limits. No paid fallback was used.",
            503,
            "PROVIDER_QUOTA_EXCEEDED",
        ),
        403: (
            "The provider denied this model request under its account or access policy. Choose another permitted free model.",
            403,
            "MODEL_NOT_ALLOWED",
        ),
        404: (
            "This model is unavailable or blocked by your provider account settings. Choose another permitted model.",
            502,
            "MODEL_UNAVAILABLE",
        ),
        408: (
            "The inference service timed out. Saved tool results remain available.",
            504,
            "PROVIDER_TIMEOUT",
        ),
        429: (
            "The free model provider is busy or its request allowance is exhausted. Try another permitted free model in Connections, or retry later.",
            429,
            "RATE_LIMITED",
        ),
        503: (
            "The inference provider is currently unavailable. Direct tools remain available.",
            503,
            "PROVIDER_UNAVAILABLE",
        ),
        504: (
            "The inference service timed out. Saved tool results remain available.",
            504,
            "PROVIDER_TIMEOUT",
        ),
    }
    message, http_status, code = errors.get(
        status,
        (
            "The inference service returned an unsuccessful response.",
            502,
            "PROVIDER_ERROR",
        ),
    )
    return AppError(message, http_status, code)


def _normalize(raw, requested_model, elapsed_ms):
    if isinstance(raw, dict) and "error" in raw:
        detail = raw["error"]
        status = detail.get("code") if isinstance(detail, dict) else None
        try:
            status = int(status) if not isinstance(status, bool) else None
        except (ValueError, TypeError, OverflowError):
            status = None
        raise provider_error(status)
    try:
        choices = raw["choices"]
        if not isinstance(choices, list) or not choices:
            raise ValueError()
        message = choices[0]["message"]
        if not isinstance(message, dict):
            raise ValueError()
        content = message.get("content")
        calls = message.get("tool_calls", [])
        if calls is None:
            calls = []
        if content is not None and (
            not isinstance(content, str) or len(content) > 8000
        ):
            raise ValueError()
        if not isinstance(calls, list) or len(calls) > 8:
            raise ValueError()
        if not calls and (not isinstance(content, str) or not content.strip()):
            raise ValueError()
        for call in calls:
            function = call["function"]
            if (
                not isinstance(function, dict)
                or not isinstance(function.get("name"), str)
                or not 1 <= len(function["name"]) <= 100
            ):
                raise ValueError()
            if (
                not isinstance(function.get("arguments"), str)
                or len(function["arguments"]) > 16000
            ):
                raise ValueError()
        model = text(raw.get("model", requested_model), "provider model", 160)
        usage = {}
        reported_usage = raw.get("usage", {})
        if isinstance(reported_usage, dict):
            for field in ["prompt_tokens", "completion_tokens", "total_tokens", "cost"]:
                value = reported_usage.get(field)
                if (
                    not isinstance(value, bool)
                    and isinstance(value, (int, float))
                    and 0 <= value <= 1_000_000_000_000
                    and math.isfinite(value)
                ):
                    usage[field] = value
        return CompletionResult(
            {"content": content, "tool_calls": deepcopy(calls)},
            model,
            usage,
            elapsed_ms,
        )
    except (KeyError, IndexError, TypeError, AttributeError, ValueError, AppError):
        raise AppError(
            "The model returned an unsupported response. Please retry.",
            502,
            "INVALID_MODEL_OUTPUT",
        ) from None


def _complete(adapter, request, token_field, extra=None):
    if not isinstance(request, CompletionRequest):
        raise AppError("Use a CompletionRequest.")
    payload = {
        "model": adapter.profile.model,
        "messages": deepcopy(request.messages),
        "tools": deepcopy(request.tools),
        "tool_choice": request.tool_choice,
        token_field: request.max_tokens,
        **(extra or {}),
    }
    if adapter.transport is None:
        from .integrations import post_json

        transport = post_json
    else:
        transport = adapter.transport
    started = time.monotonic()
    try:
        raw = transport(adapter.endpoint, payload, adapter._key)
        result = _normalize(
            raw, adapter.profile.model, max(0, int((time.monotonic() - started) * 1000))
        )
    except AppError as error:
        if adapter.on_result:
            adapter.on_result(
                adapter.profile,
                error=error,
                elapsed_ms=max(0, int((time.monotonic() - started) * 1000)),
            )
        raise
    if adapter.on_result:
        adapter.on_result(adapter.profile, elapsed_ms=result.elapsed_ms)
    return result


class OpenRouterAdapter:
    def __init__(self, key, model, transport=None, on_result=None):
        if not key:
            raise AppError(
                "The free AI connection is not configured yet.", 503, "NOT_CONFIGURED"
            )
        if key.startswith("sk-nous-"):
            raise AppError(
                "Use the credential belonging to this inference provider.",
                503,
                "CONFIGURATION_ERROR",
            )
        self.profile = ModelProfile("openrouter", free_model(model))
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self._key, self.transport, self.on_result = key, transport, on_result

    def complete(self, request):
        return _complete(
            self, request, "max_tokens", {"provider": {"require_parameters": True}}
        )


class MetaAdapter:
    """Existing local Meta route; contract-tested, live access remains unverified."""

    def __init__(
        self,
        key,
        model,
        base_url="https://api.meta.ai/v1",
        transport=None,
        on_result=None,
    ):
        if not key:
            raise AppError(
                "Set MODEL_API_KEY locally and restart to enable Muse.",
                503,
                "NOT_CONFIGURED",
            )
        try:
            parsed = urlsplit(base_url)
            host = (parsed.hostname or "").lower().rstrip(".")
            parsed.port
        except (ValueError, TypeError, AttributeError):
            raise AppError(
                "Invalid endpoint for the Meta adapter.", 503, "CONFIGURATION_ERROR"
            ) from None
        if (
            key.startswith(("sk-or-", "sk-nous-"))
            or not host
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or host == "openrouter.ai"
            or host.endswith(".openrouter.ai")
            or host == "nousresearch.com"
            or host.endswith(".nousresearch.com")
            or not (
                parsed.scheme == "https"
                or (
                    parsed.scheme == "http"
                    and host in {"127.0.0.1", "localhost", "::1"}
                )
            )
        ):
            raise AppError(
                "Invalid endpoint or credential for the Meta adapter.",
                503,
                "CONFIGURATION_ERROR",
            )
        self.profile = ModelProfile("meta", text(model, "Meta model", 160))
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self._key, self.transport, self.on_result = key, transport, on_result

    def complete(self, request):
        return _complete(self, request, "max_completion_tokens")
