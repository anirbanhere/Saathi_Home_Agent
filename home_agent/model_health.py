"""Bounded process-local model request observations, never prompts or account data."""

from collections import OrderedDict
from datetime import datetime, timezone
import threading
import time


class ModelHealth:
    def __init__(self, clock=time.monotonic, ttl=300, max_entries=64):
        self.clock, self.ttl, self.max_entries = clock, ttl, max_entries
        self.entries = OrderedDict()
        self.lock = threading.Lock()

    def record(self, profile, *, error=None, elapsed_ms=0):
        code = error.code if error else None
        state = {
            "RATE_LIMITED": "rate_limited",
            "MODEL_AUTH_ERROR": "auth_error",
            "MODEL_NOT_ALLOWED": "permission_denied",
            "INVALID_MODEL_OUTPUT": "invalid_response",
        }.get(code, "unavailable" if error else "responding")
        # Only stable app codes are retained, not raw exception/provider text.
        allowed_codes = {
            "RATE_LIMITED",
            "MODEL_AUTH_ERROR",
            "MODEL_NOT_ALLOWED",
            "INVALID_MODEL_OUTPUT",
            "MODEL_UNAVAILABLE",
            "PROVIDER_QUOTA_EXCEEDED",
            "PROVIDER_TIMEOUT",
            "PROVIDER_UNAVAILABLE",
            "PROVIDER_ERROR",
        }
        entry = {
            "provider": profile.provider,
            "model": profile.model,
            "state": state,
            "error_code": (
                code if code in allowed_codes else "PROVIDER_ERROR" if error else None
            ),
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "elapsed_ms": elapsed_ms,
        }
        with self.lock:
            key = (profile.provider, profile.model)
            self.entries[key] = (self.clock(), entry)
            self.entries.move_to_end(key)
            while len(self.entries) > self.max_entries:
                self.entries.popitem(last=False)

    def status(self, profile):
        with self.lock:
            saved = self.entries.get((profile.provider, profile.model))
            if saved:
                stamp, entry = saved
                result = dict(entry)
                if self.clock() - stamp >= self.ttl:
                    result["last_state"] = result["state"]
                    result["state"] = "stale"
            else:
                result = {
                    "provider": profile.provider,
                    "model": profile.model,
                    "state": "unobserved",
                    "error_code": None,
                    "checked_at": None,
                    "elapsed_ms": None,
                }
        result["message"] = {
            "unobserved": "Key access is configured; no model request has been observed in this application process yet.",
            "responding": "The last model request responded; this is not a guarantee of task success or future availability.",
            "rate_limited": "The last model request was rate-limited. Retry later or choose another permitted free model; direct tools remain available.",
            "auth_error": "The provider rejected its server credential; direct tools remain available.",
            "permission_denied": "The provider denied the last request under its access policy; refresh permitted model choices.",
            "invalid_response": "The last model response could not be used. No successful task is implied.",
            "unavailable": "The last model request failed or was unavailable; saved observations and direct tools remain available.",
            "stale": "The last model request observation is no longer recent; current inference availability is unverified.",
        }[result["state"]]
        result["scope"] = (
            "Process-local observation, not an active probe or persistent uptime history."
        )
        return result
