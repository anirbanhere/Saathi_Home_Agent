"""Private worker client. Only URLs/actions cross this boundary; no household/API secrets."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

from .browser_policy import public_url, validate_actions
from .errors import AppError
from .integrations import NoRedirect


class BrowserClient:
    def __init__(self, endpoint=None, transport=None, before_request=None):
        self.endpoint = (
            os.environ.get("HOME_AGENT_BROWSER_WORKER_URL", "")
            if endpoint is None
            else endpoint
        ).rstrip("/")
        self.transport = transport
        self.before_request = before_request or (lambda: None)

    @property
    def configured(self):
        return bool(self.endpoint or self.transport)

    def observe(self, url, actions=None):
        url, actions = public_url(url), validate_actions(actions or [])
        if not self.configured:
            raise AppError(
                "The public browser worker is not connected yet.",
                503,
                "BROWSER_NOT_CONFIGURED",
            )
        self.before_request()
        if self.transport:
            result = self.transport({"url": url, "actions": actions})
        else:
            parsed = urlsplit(self.endpoint)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or not parsed.hostname.endswith(".run.app")
                or parsed.path
                or parsed.username
                or parsed.password
                or parsed.port not in {None, 443}
                or parsed.query
                or parsed.fragment
            ):
                raise AppError(
                    "Browser worker endpoint configuration is invalid.",
                    503,
                    "CONFIGURATION_ERROR",
                )
            from google.auth.transport.requests import Request as GoogleRequest
            from google.oauth2.id_token import fetch_id_token

            try:
                token = fetch_id_token(GoogleRequest(), self.endpoint)
            except Exception:
                raise AppError(
                    "The application could not authenticate to its private browser worker.",
                    503,
                    "BROWSER_AUTH_UNAVAILABLE",
                ) from None
            request = Request(
                self.endpoint + "/observe",
                data=json.dumps({"url": url, "actions": actions}).encode(),
                headers={
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/json",
                },
            )
            try:
                with build_opener(NoRedirect).open(request, timeout=90) as response:
                    body = response.read(200001)
                if len(body) > 200000:
                    raise ValueError()
                result = json.loads(body)
            except HTTPError as error:
                try:
                    detail = json.loads(error.read(4000)).get("error", {})
                    code, message = detail.get("code"), detail.get("message")
                    if (
                        isinstance(code, str)
                        and code.startswith("BROWSER_")
                        and isinstance(message, str)
                        and len(message) < 600
                    ):
                        raise AppError(message, 502, code)
                except (ValueError, TypeError, AttributeError):
                    pass
                raise AppError(
                    "The browser service could not read the page. Try another public source.",
                    502,
                    "BROWSER_UNAVAILABLE",
                ) from None
            except (URLError, OSError, ValueError):
                raise AppError(
                    "The browser service is unavailable or timed out.",
                    502,
                    "BROWSER_UNAVAILABLE",
                ) from None
        if (
            not isinstance(result, dict)
            or result.get("profile") != "public_readonly"
            or result.get("state") not in {"observed", "needs_input"}
        ):
            raise AppError(
                "The browser returned an invalid observation.",
                502,
                "BROWSER_INVALID_RESPONSE",
            )
        for key, limit in [("text", 12000), ("title", 300), ("observed_at", 60)]:
            if not isinstance(result.get(key), str) or len(result[key]) > limit:
                raise AppError(
                    "The browser returned an invalid observation.",
                    502,
                    "BROWSER_INVALID_RESPONSE",
                )
        result["url"] = public_url(result.get("url"))
        if (
            not isinstance(result.get("controls", []), list)
            or len(result.get("controls", [])) > 40
            or not isinstance(result.get("links", []), list)
            or len(result.get("links", [])) > 35
        ):
            raise AppError(
                "The browser returned oversized controls/links.",
                502,
                "BROWSER_INVALID_RESPONSE",
            )
        links = []
        for link in result.get("links", []):
            if (
                isinstance(link, dict)
                and isinstance(link.get("title"), str)
                and len(link["title"]) <= 120
            ):
                try:
                    links.append(
                        {"title": link["title"], "url": public_url(link.get("url"))}
                    )
                except AppError:
                    pass
        result["links"] = links
        for control in result.get("controls", []):
            if not isinstance(control, dict) or any(
                not isinstance(control.get(field), str) or len(control[field]) > limit
                for field, limit in [
                    ("selector", 250),
                    ("label", 120),
                    ("tag", 20),
                    ("type", 40),
                ]
            ):
                raise AppError(
                    "The browser returned invalid controls.",
                    502,
                    "BROWSER_INVALID_RESPONSE",
                )
        # Only data needed for this research task returns to the main runtime.
        return {
            key: result[key]
            for key in [
                "url",
                "title",
                "text",
                "observed_at",
                "profile",
                "state",
                "controls",
                "links",
                "notice",
                "actions",
                "http_status",
            ]
            if key in result
        }
