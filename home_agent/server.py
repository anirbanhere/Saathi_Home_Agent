"""Loopback-only demo server. Not a public or production HTTP deployment."""
import json
import logging
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .errors import AppError, text
from .integrations import MusePlanner, speech_request
from .service import HomeAgent

STATIC = Path(__file__).resolve().parent.parent / "web"
FILES = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"),
         "/styles.css": ("styles.css", "text/css; charset=utf-8"), "/favicon.svg": ("favicon.svg", "image/svg+xml")}
LOG = logging.getLogger("home-agent")


def integrations():
    return {"muse": bool(os.environ.get("MODEL_API_KEY")), "asr": bool(os.environ.get("HOME_AGENT_ASR_URL")),
            "tts": bool(os.environ.get("HOME_AGENT_TTS_URL")), "hermes": "MCP adapter available; not connected by this server",
            "whatsapp": "Not connected", "travel": "Local fixtures", "payments": "Local sandbox",
            "model": os.environ.get("META_MODEL", "muse-spark-1.3")}


class Handler(BaseHTTPRequestHandler):
    server_version = "HomeAgent/0.1"

    def setup(self):
        super().setup()
        self.connection.settimeout(60)

    def log_message(self, fmt, *args):
        # Do not log user text, request bodies, credentials, or query strings.
        LOG.info("%s %s", self.command, urlsplit(self.path).path)

    def respond(self, status, data, content_type="application/json; charset=utf-8"):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; media-src 'self' blob: data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)

    def check_local(self, mutation=False):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in hosts:
            raise AppError("Only the local console host is accepted.", 403, "FORBIDDEN")
        origin = self.headers.get("Origin")
        if origin and origin not in {"http://" + host for host in hosts}:
            raise AppError("Cross-origin requests are not allowed.", 403, "FORBIDDEN")
        if mutation and self.headers.get("X-Home-Agent") != "local-console":
            raise AppError("Local-console request header required.", 403, "FORBIDDEN")

    def body(self):
        if self.headers.get("Transfer-Encoding"):
            raise AppError("Chunked requests are not supported.", 400, "BAD_REQUEST")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise AppError("Invalid content length.", 400, "BAD_REQUEST") from None
        if not 0 < length <= 8_000_000:
            raise AppError("Request body must be between 1 byte and 8 MB.", 413, "TOO_LARGE")
        if self.headers.get_content_type() != "application/json":
            raise AppError("Use application/json.", 415, "UNSUPPORTED_MEDIA_TYPE")
        try:
            data = json.loads(self.rfile.read(length), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (ValueError, UnicodeError):
            raise AppError("Request must contain valid UTF-8 JSON.") from None
        if not isinstance(data, dict):
            raise AppError("Request body must be a JSON object.")
        return data

    def guarded(self, operation):
        try:
            operation()
        except AppError as error:
            self.respond(error.status, {"error": {"code": error.code, "message": str(error)}})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except sqlite3.OperationalError:
            self.respond(503, {"error": {"code": "STORAGE_UNAVAILABLE", "message": "Local storage is temporarily unavailable. Try again."}})
        except Exception:
            LOG.exception("Local request failed")
            self.respond(500, {"error": {"code": "INTERNAL_ERROR", "message": "Unexpected local error. Check the server terminal."}})

    def do_GET(self):
        self.guarded(self.get)

    def get(self):
        self.check_local()
        parsed = urlsplit(self.path)
        if parsed.path == "/api/state":
            session = text(parse_qs(parsed.query).get("session", ["demo"])[0], "session", 100)
            result = self.server.agent.snapshot(session=session)
            result["integrations"] = integrations()
            self.respond(200, result)
        elif parsed.path == "/api/health":
            self.respond(200, {"status": "ok", "local_only": True})
        elif parsed.path in FILES:
            name, mime = FILES[parsed.path]
            self.respond(200, (STATIC / name).read_bytes(), mime)
        else:
            raise AppError("Not found.", 404, "NOT_FOUND")

    def do_POST(self):
        self.guarded(self.post)

    def post(self):
        self.check_local(mutation=True)
        data = self.body()
        route = urlsplit(self.path).path
        app = self.server.agent
        if route == "/api/messages":
            engine = data.get("engine", "offline")
            content = text(data.get("text"), "message", 4000)
            language = text(data.get("language", "en"), "language", 2)
            session = text(data.get("session", "demo"), "session", 100)
            request_id = text(data.get("request_id", ""), "request id", 100, allow_empty=True) or None
            if engine == "muse":
                result = MusePlanner().message(app, content, language, session, request_id)
            elif engine == "offline":
                result = app.message(content, language, session, request_id)
            else:
                raise AppError("Choose offline or muse engine.")
        elif route == "/api/tools":
            name = text(data.get("name"), "tool name", 40)
            result = app.tool(name, data.get("arguments", {}))
        elif route == "/api/receipts":
            result = app.import_receipt(data.get("text"), data.get("reference"))
        elif route == "/api/inventory/corrections":
            result = app.correct_stock(data.get("name"), data.get("quantity"), data.get("unit"), data.get("reference"))
        elif route in {"/api/speech/transcriptions", "/api/speech/syntheses"}:
            result = speech_request("transcribe" if route.endswith("transcriptions") else "synthesize", data)
        elif (match := re.fullmatch(r"/api/tasks/([a-f0-9]{32})/(approval|cancellation|completion)", route)):
            methods = {"approval": app.approve, "cancellation": app.cancel, "completion": app.complete_meal}
            result = methods[match[2]](match[1])
        else:
            raise AppError("Not found.", 404, "NOT_FOUND")
        self.respond(200, result)

    def do_OPTIONS(self):
        self.respond(405, {"error": {"code": "METHOD_NOT_ALLOWED", "message": "Cross-origin preflight is not supported."}})


def make_server(agent=None, port=8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.agent = agent or HomeAgent()
    server.daemon_threads = True
    return server
