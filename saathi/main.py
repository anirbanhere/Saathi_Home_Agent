"""Local-only mock API. No public WhatsApp/provider webhook or real execution routes."""

import hashlib
import secrets
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from .config import Settings
from .contracts import Contract, InboundMessage, Locale, OutboundMessage
from .channels import LocalChannel
from .db import Store, schema as s
from .runtime import Runtime, DomainError
from .providers import ProviderRouter
from .speech import fixture_audio
from .registry import ToolRegistry, MockAppointmentTool
from .http_limits import BodyLimit
from .observability import configure_logging
from .media import MediaStore, MAX_BYTES
from .media_routes import register_media_routes
from pydantic import Field
import base64

WEB = Path(__file__).resolve().parents[1] / "saathi_web"
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
}


class NewSession(Contract):
    locale: Locale = "en-IN"
    consent_mock_data: Literal[True]


class SlotChoice(Contract):
    slot_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    version: int = Field(ge=0, strict=True)


class Version(Contract):
    version: int = Field(ge=0, strict=True)


class Decision(Version):
    decision: Literal["approve", "reject", "edit"]
    token: str = Field(min_length=20, max_length=100)


def create_app(settings=None, store=None):
    configure_logging()
    settings = settings or Settings.load()
    store = store or Store(settings.database_url)
    runtime = Runtime(store, settings)
    app = FastAPI(title="Saathi — local mock reference", docs_url=None, redoc_url=None)
    app.state.runtime = runtime
    media = MediaStore(store, settings)
    app.state.media = media
    app.add_middleware(BodyLimit, limits_by_path={"/api/media": MAX_BYTES})
    register_media_routes(app, media)
    registry = ToolRegistry()
    registry.register(MockAppointmentTool(runtime))
    events = deque()

    def error(message, code, status):
        return JSONResponse(
            {"error": {"code": code, "message": message}},
            status_code=status,
            headers=SECURITY_HEADERS,
        )

    @app.middleware("http")
    async def boundary(request, call_next):
        # This initial identity/media boundary is deliberately limited to loopback.
        if request.url.hostname not in {"127.0.0.1", "localhost", "::1"}:
            return error("Phase1 web service is loopback-only.", "LOCAL_ONLY", 403)
        uploading_audio = request.method == "POST" and request.url.path == "/api/media"
        maximum = MAX_BYTES if uploading_audio else 60000
        if (
            request.headers.get("content-length", "0").isdigit()
            and int(request.headers.get("content-length", "0")) > maximum
        ):
            return error(
                "Request exceeds the allowed byte limit.", "PAYLOAD_LIMIT", 413
            )
        if request.method in {"POST", "DELETE", "PATCH", "PUT"}:
            origin = f"{request.url.scheme}://{request.url.netloc}"
            if request.headers.get("origin") != origin or request.headers.get(
                "content-type", ""
            ).split(";")[0] != ("audio/wav" if uploading_audio else "application/json"):
                return error(
                    "Use a same-origin request with the expected content type.",
                    "ORIGIN_DENIED",
                    403,
                )
            now = datetime.now(timezone.utc).timestamp()
            while events and events[0] < now - 60:
                events.popleft()
            if len(events) >= 100:
                return error("Local demo request budget reached.", "RATE_LIMITED", 429)
            events.append(now)
        if request.url.path.startswith("/api/") and request.url.path != "/api/session":
            raw = request.cookies.get("saathi_local", "")
            token_hash = hashlib.sha256(raw.encode()).hexdigest()
            with store.transaction() as c:
                session = (
                    c.execute(
                        select(s.sessions).where(s.sessions.c.token_hash == token_hash)
                    )
                    .mappings()
                    .first()
                )
            if (
                not raw
                or not session
                or datetime.fromisoformat(session["expires_at"])
                <= datetime.now(timezone.utc)
            ):
                return error("Start a local mock session.", "UNAUTHORIZED", 401)
            if request.method != "GET" and not secrets.compare_digest(
                request.headers.get("x-saathi-csrf", ""), session["csrf"]
            ):
                return error("Invalid session action token.", "CSRF_DENIED", 403)
            request.state.user = session["user_id"]
        response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
            }
        )
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request, exc):
        return error(str(exc), exc.code, exc.status)

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error(
            (
                "Request exceeds the allowed byte limit."
                if exc.status_code == 413
                else "Unsupported request or route."
            ),
            "PAYLOAD_LIMIT" if exc.status_code == 413 else "HTTP_ERROR",
            exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        return error("Invalid or unsupported request fields.", "INVALID_INPUT", 422)

    @app.exception_handler(ValueError)
    async def invalid_value(request, exc):
        return error(
            "Unsupported input/provider configuration. Use a supported mock fixture or text.",
            "UNSUPPORTED_INPUT",
            422,
        )

    @app.exception_handler(SQLAlchemyError)
    async def storage_error(request, exc):
        return error(
            "Storage operation failed; reload current state before retrying.",
            "STORAGE_UNAVAILABLE",
            503,
        )

    @app.get("/health/live")
    def live():
        return {
            "status": "ok",
            "mode": "mock",
            "whatsapp_production_eligible": False,
            "live_actions_enabled": False,
        }

    @app.get("/health/ready")
    def ready():
        try:
            with store.engine.connect() as c:
                c.execute(text("SELECT 1"))
            if settings.redis_url:
                import redis

                redis.Redis.from_url(settings.redis_url, socket_timeout=2).ping()
        except Exception:
            return error(
                "Configured storage/cache dependency is unavailable.", "NOT_READY", 503
            )
        return {
            "status": "ready",
            "database": store.engine.dialect.name,
            "redis": "checked" if settings.redis_url else "not_configured",
            "mode": "mock",
        }

    @app.post("/api/session")
    def start(body: NewSession, request: Request):
        user = runtime.create_user(body.locale)
        raw, csrf = secrets.token_urlsafe(32), secrets.token_hex(32)
        with store.transaction(user) as c:
            c.execute(
                s.sessions.insert().values(
                    token_hash=hashlib.sha256(raw.encode()).hexdigest(),
                    user_id=user,
                    csrf=csrf,
                    expires_at=(
                        datetime.now(timezone.utc) + timedelta(hours=24)
                    ).isoformat(),
                )
            )
        response = JSONResponse({"csrf": csrf, "mock": True, "locale": body.locale})
        response.set_cookie(
            "saathi_local",
            raw,
            httponly=True,
            samesite="strict",
            secure=request.url.scheme == "https",
            max_age=86400,
            path="/",
        )
        return response

    @app.get("/api/session")
    def session(request: Request):
        raw = request.cookies.get("saathi_local", "")
        with store.transaction() as c:
            row = (
                c.execute(
                    select(s.sessions).where(
                        s.sessions.c.token_hash
                        == hashlib.sha256(raw.encode()).hexdigest()
                    )
                )
                .mappings()
                .first()
            )
            if not row or datetime.fromisoformat(row["expires_at"]) <= datetime.now(
                timezone.utc
            ):
                return {"active": False, "mock": True}
            locale = c.scalar(
                select(s.users.c.locale).where(s.users.c.id == row["user_id"])
            )
        return {"active": True, "csrf": row["csrf"], "locale": locale, "mock": True}

    @app.get("/api/provider-connections")
    def providers():
        return {
            "profiles": ProviderRouter(settings.profiles()).snapshot(),
            "mode": "mock",
            "whatsapp_production_eligible": False,
            "live_speech_enabled": False,
        }

    @app.post("/api/chat/messages")
    async def message(body: InboundMessage, request: Request):
        if body.channel != "web_chat":
            raise DomainError(
                "This endpoint only accepts the web channel.", "INVALID_CHANNEL", 422
            )
        channel = LocalChannel("web_chat")
        normalized = await channel.normalize_inbound(body.model_dump())
        result = await runtime.handle(request.state.user, normalized)
        await channel.send_message(
            OutboundMessage(
                task_id=result["id"],
                text=result["payload"]["reply"],
                locale=result["locale"],
            )
        )
        return result

    @app.get("/api/tasks")
    def tasks(request: Request):
        return runtime.list_tasks(request.state.user)

    @app.get("/api/tools/catalog")
    def catalog():
        return registry.manifest()

    @app.get("/api/tasks/{task_id}")
    def task(task_id: str, request: Request):
        return runtime.get(request.state.user, task_id)

    @app.post("/api/tasks/{task_id}/preview")
    async def preview(task_id: str, body: SlotChoice, request: Request):
        return await registry.invoke(
            "appointments.book",
            "prepare",
            {"task_id": task_id, **body.model_dump()},
            {"user_id": request.state.user},
        )

    @app.post("/api/approvals/{approval_id}/decision")
    async def decide(approval_id: str, body: Decision, request: Request):
        if body.decision != "approve":
            return runtime.decide(
                request.state.user, approval_id, body.decision, body.token, body.version
            )
        with store.transaction(request.state.user) as c:
            task_id = c.scalar(
                select(s.approvals.c.task_id).where(
                    s.approvals.c.id == approval_id,
                    s.approvals.c.user_id == request.state.user,
                )
            )
        if not task_id:
            raise DomainError("Approval not found.", "NOT_FOUND", 404)
        return await registry.invoke(
            "appointments.book",
            "execute",
            {"task_id": task_id, "approval_id": approval_id, "version": body.version},
            {
                "user_id": request.state.user,
                "human_approval": True,
                "approval_token": body.token,
            },
        )

    @app.post("/api/tasks/{task_id}/cancel")
    def cancel(task_id: str, body: Version, request: Request):
        return runtime.cancel(request.state.user, task_id, body.version)

    @app.post("/api/tasks/{task_id}/reconcile")
    def reconcile(task_id: str, body: Version, request: Request):
        return runtime.reconcile(request.state.user, task_id, body.version)

    @app.get("/api/fixtures/{locale}")
    def fixture(locale: Locale):
        return {
            "audio_base64": base64.b64encode(fixture_audio(locale)).decode(),
            "mime": "audio/wav",
            "notice": "Synthetic acoustic token, not a spoken recording or ASR benchmark.",
        }

    @app.get("/api/tasks/{task_id}/audio")
    async def audio(task_id: str, request: Request):
        task = runtime.get(request.state.user, task_id)
        router = ProviderRouter(task["profiles"])
        result = await router.tts.synthesize(task["payload"]["reply"], task["locale"])
        return {
            **result.model_dump(),
            "notice": "Mock TTS emits a synthetic tone, not a spoken reply.",
        }

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html")

    @app.get("/assets/{name}")
    def asset(name: Literal["app.js", "style.css", "media.js"]):
        return FileResponse(WEB / name)

    return app
