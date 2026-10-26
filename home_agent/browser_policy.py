"""Public read-only browser boundaries, independent of model instructions."""

import ipaddress
import re
import socket
from urllib.parse import parse_qsl, urlsplit, urlunsplit, unquote

from .errors import AppError

WRITE_PATH = re.compile(
    r"(?:^|/)(?:login|signin|sign-in|signup|sign-up|account|auth|oauth|checkout|payment|pay|purchase|delete|unsubscribe)(?:/|$)|/(?:cart/add|orders/submit)",
    re.I,
)
SECRET_QUERY = {
    "access_token",
    "api_key",
    "apikey",
    "password",
    "secret",
    "session",
    "signature",
    "token",
    "authorization",
}
COMMIT_TEXT = re.compile(
    r"\b(pay|purchase|buy|place order|confirm order|delete|send message|sign in|log in|subscribe)\b",
    re.I,
)


def public_url(value):
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= 2000
        or any(ord(c) < 32 for c in value)
    ):
        raise AppError("Use a public HTTPS page URL.", 422, "BROWSER_URL_BLOCKED")
    try:
        parsed = urlsplit(value)
        hostname = (
            (parsed.hostname or "").rstrip(".").encode("idna").decode("ascii").lower()
        )
        port = parsed.port
    except (ValueError, UnicodeError):
        raise AppError("Invalid browser URL.", 422, "BROWSER_URL_BLOCKED") from None
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or not hostname
    ):
        raise AppError(
            "Only public HTTPS URLs without credentials or custom ports are supported.",
            422,
            "BROWSER_URL_BLOCKED",
        )
    if hostname in {"localhost", "metadata.google.internal"} or hostname.endswith(
        (".localhost", ".internal", ".local")
    ):
        raise AppError(
            "Private/local addresses are blocked.", 422, "BROWSER_URL_BLOCKED"
        )
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise AppError(
            "Private/reserved addresses are blocked.", 422, "BROWSER_URL_BLOCKED"
        )
    if WRITE_PATH.search(unquote(parsed.path)) or any(
        key.lower() in SECRET_QUERY for key, _ in parse_qsl(parsed.query)
    ):
        raise AppError(
            "Account, payment or credential-bearing pages require a secure user handoff.",
            422,
            "BROWSER_HANDOFF_REQUIRED",
        )
    return urlunsplit(("https", parsed.netloc, parsed.path or "/", parsed.query, ""))


def public_addresses(hostname, resolver=socket.getaddrinfo):
    try:
        records = resolver(hostname, 443, type=socket.SOCK_STREAM)
        addresses = list(dict.fromkeys(record[4][0] for record in records))
    except OSError:
        raise AppError(
            "The public website could not be resolved.", 502, "BROWSER_DNS_ERROR"
        ) from None
    if not addresses or any(
        not ipaddress.ip_address(value).is_global for value in addresses
    ):
        raise AppError(
            "The website resolves to a private/reserved address.",
            422,
            "BROWSER_URL_BLOCKED",
        )
    return addresses


def validate_actions(actions):
    if not isinstance(actions, list) or len(actions) > 6:
        raise AppError("At most six read-only browser actions are accepted.")
    for action in actions:
        if not isinstance(action, dict) or action.get("type") not in {
            "fill",
            "click",
            "select",
        }:
            raise AppError(
                "Only structured fill, click and select actions are supported.",
                422,
                "BROWSER_ACTION_BLOCKED",
            )
        keys = (
            {"type", "selector"}
            if action["type"] == "click"
            else {"type", "selector", "value"}
        )
        if (
            set(action) != keys
            or not isinstance(action.get("selector"), str)
            or not 1 <= len(action["selector"]) <= 250
        ):
            raise AppError(
                "Invalid browser action schema.", 422, "BROWSER_ACTION_BLOCKED"
            )
        if action["type"] != "click":
            value = action["value"]
            if (
                not isinstance(value, str)
                or len(value) > 200
                or any(mark in value for mark in ["sk-or-", "rr_live_", "ghp_", "gho_"])
            ):
                raise AppError(
                    "Browser fields accept short public lookup values, never credentials.",
                    422,
                    "BROWSER_ACTION_BLOCKED",
                )
    return actions
