"""Public demo boundary: isolated visitors, strict origin, durable tools, free AI."""
import os
import re
import secrets
import threading
import time
from collections import defaultdict, deque
from urllib.parse import urlsplit

from flask import Flask, g, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from .agent_loop import FreeModelAgent, free_model
from .cloud_state import VisitorState
from .errors import AppError, text
from .server import STATIC
from .model_catalog import ModelCatalog
from .trains import configuration as train_configuration

COOKIE = "__Host-home-agent"
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"


class Limits:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = defaultdict(deque)

    def consume(self, name, count, window):
        stamp = time.monotonic()
        with self.lock:
            events = self.events[name]
            while events and events[0] <= stamp-window:
                events.popleft()
            if len(events) >= count:
                raise AppError("The demo is busy or its free-model allowance is used. Please try later.", 429, "RATE_LIMITED")
            events.append(stamp)


def create_app(repository=None, model_catalog=None):
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = 32_000
    repository = repository or VisitorState()
    model_catalog = model_catalog or ModelCatalog()
    limits = Limits()

    def model_budget():
        limits.consume("model-minute", 15, 60)
        limits.consume("model-day", 45, 86400)

    @app.before_request
    def boundary():
        if not request.path.startswith("/api/") or request.path == "/api/health":
            return
        limits.consume("api", 300, 60)
        origin = request.headers.get("Origin")
        host = urlsplit(origin).netloc if origin else ""
        configured = os.environ.get("HOME_AGENT_PUBLIC_ORIGIN", "")
        if origin and ((configured and origin != configured) or host != request.host or urlsplit(origin).scheme not in {"https", "http"}):
            raise AppError("Cross-origin requests are not allowed.", 403, "FORBIDDEN")
        token = request.cookies.get(COOKIE, "")
        valid = bool(re.fullmatch(r"[a-f0-9]{64}", token))
        if request.method != "GET":
            if not valid or not origin or request.headers.get("X-Home-Agent") != "local-console":
                raise AppError("Open this website to initialize your private demo workspace.", 403, "FORBIDDEN")
            if request.mimetype != "application/json":
                raise AppError("Use application/json.", 415, "UNSUPPORTED_MEDIA_TYPE")
        g.visitor = token if valid else secrets.token_hex(32)
        g.new_visitor = not valid

    @app.after_request
    def headers(response):
        response.headers.update({
            "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer", "Strict-Transport-Security": "max-age=31536000",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; media-src 'self' blob: data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        })
        if getattr(g, "new_visitor", False) and response.status_code < 400:
            response.set_cookie(COOKIE, g.visitor, max_age=604800, secure=True, httponly=True, samesite="Lax", path="/")
        return response

    @app.errorhandler(AppError)
    def app_error(error):
        return jsonify(error={"code": error.code, "message": str(error)}), error.status

    @app.errorhandler(Exception)
    def unexpected(error):
        if isinstance(error, HTTPException):
            return jsonify(error={"code": error.name.upper().replace(" ", "_"), "message": error.description}), error.code
        # Record the type without request bodies, user text, credentials or provider output.
        app.logger.error("Hosted request failed: %s", type(error).__name__)
        return jsonify(error={"code": "SERVICE_UNAVAILABLE", "message": "The service is temporarily unavailable. Please retry."}), 503

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", hosted=True, free_models_only=True)

    @app.get("/api/state")
    def state():
        session = text(request.args.get("session", "demo"), "session", 100)
        with repository.open(g.visitor) as agent:
            result = agent.snapshot(session=session)
        catalog = model_catalog.status(os.environ.get("OPENROUTER_API_KEY", ""))
        preferred = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
        selected = preferred if preferred in catalog["models"] else next(iter(catalog["models"]), "")
        result["integrations"] = {
            "hosted": True, "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")), "muse": False,
            "model": selected, "models": catalog["models"], "model_catalog": catalog,
            "asr": False, "tts": False, "hermes": "Not connected; bounded application tool loop active",
            "whatsapp": "Not connected", "travel": "Live provider adapter" if train_configuration()["configured"] else "Train provider not connected" if train_configuration()["provider"] == "railradar" else "Sample data", "payments": "Sandbox",
            "train": train_configuration(),
            "storage": "Private Cloud Storage snapshots" if repository.bucket_name else "Local visitor storage",
        }
        return jsonify(result)

    @app.post("/api/<path:route>")
    def mutate(route):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise AppError("Request body must be a JSON object.")
        with repository.open(g.visitor, write=True) as agent:
            if route == "messages":
                with agent.store.transaction() as db:
                    if db.execute("SELECT COUNT(*) FROM messages").fetchone()[0] >= 100:
                        raise AppError("This demo workspace has reached 100 messages.", 429, "WORKSPACE_LIMIT")
                content = text(data.get("text"), "message", 4000)
                language = text(data.get("language", "en"), "language", 2)
                session = text(data.get("session", "demo"), "session", 100)
                request_id = text(data.get("request_id", ""), "request id", 100, allow_empty=True) or None
                engine = data.get("engine", "openrouter")
                if engine == "openrouter":
                    if data.get("model"):
                        free_model(data["model"])
                    catalog = model_catalog.status(os.environ.get("OPENROUTER_API_KEY", ""))
                    if not catalog["verified"] or not catalog["models"]:
                        raise AppError(catalog["message"], 503, catalog["code"])
                    preferred = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
                    model = data.get("model") or (preferred if preferred in catalog["models"] else catalog["models"][0])
                    if model not in catalog["models"]:
                        raise AppError("This model is not permitted by the configured API key. Refresh Connections and select an allowed free model. To enable it, update the key's OpenRouter guardrails.", 403, "MODEL_NOT_ALLOWED")
                    result = FreeModelAgent(model=model, before_request=model_budget).message(agent, content, language, session, request_id)
                elif engine == "offline":
                    result = agent.message(content, language, session, request_id)
                else:
                    raise AppError("Choose the free AI or offline engine.")
            elif route == "tools":
                result = agent.tool(text(data.get("name"), "tool name", 40), data.get("arguments", {}))
            elif route == "receipts":
                result = agent.import_receipt(data.get("text"), data.get("reference"))
            elif route == "inventory/corrections":
                result = agent.correct_stock(data.get("name"), data.get("quantity"), data.get("unit"), data.get("reference"))
            elif (match := re.fullmatch(r"tasks/([a-f0-9]{32})/(approval|cancellation|completion)", route)):
                methods = {"approval": agent.approve, "cancellation": agent.cancel, "completion": agent.complete_meal}
                result = methods[match[2]](match[1])
            else:
                raise AppError("Not found.", 404, "NOT_FOUND")
        # Persistence has completed before a success response is returned.
        return jsonify(result)

    @app.get("/")
    def index():
        return send_from_directory(STATIC, "index.html")

    @app.get("/<name>")
    def static_file(name):
        if name not in {"app.js", "styles.css", "favicon.svg"}:
            raise AppError("Not found.", 404, "NOT_FOUND")
        return send_from_directory(STATIC, name)

    return app
