"""Cache only free tool-capable models permitted by the configured API key."""
import hashlib
import json
import threading
import time
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from .errors import AppError
from .integrations import NoRedirect


def fetch_catalog(key):
    request = Request("https://openrouter.ai/api/v1/models/user", headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    try:
        with build_opener(NoRedirect).open(request, timeout=12) as response:
            body = response.read(8_000_001)
        if len(body) > 8_000_000:
            raise ValueError()
        return json.loads(body)
    except HTTPError as error:
        if error.code in {401, 403}:
            raise AppError("OpenRouter rejected the configured API key. Update the server credential.", 503, "MODEL_AUTH_ERROR") from None
        raise AppError("Could not verify the models permitted by the API key. Please retry shortly.", 503, "MODEL_CATALOG_UNAVAILABLE") from None
    except (URLError, OSError, ValueError):
        raise AppError("Could not verify the models permitted by the API key. Please retry shortly.", 503, "MODEL_CATALOG_UNAVAILABLE") from None


class ModelCatalog:
    def __init__(self, loader=fetch_catalog, clock=time.monotonic):
        self.loader, self.clock = loader, clock
        self.lock = threading.Lock()
        self.cached, self.expires, self.fingerprint = None, 0, ""

    def status(self, key):
        if not key:
            return {"models": [], "names": {}, "verified": False, "code": "NOT_CONFIGURED", "message": "The free AI key is not configured."}
        fingerprint = hashlib.sha256(key.encode()).hexdigest()
        with self.lock:
            stamp = self.clock()
            if self.cached is not None and stamp < self.expires and self.fingerprint == fingerprint:
                return self.cached
            try:
                payload = self.loader(key)
                entries = payload["data"]
                if not isinstance(entries, list):
                    raise ValueError()
                names = {}
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    identifier = entry.get("id")
                    parameters = entry.get("supported_parameters", [])
                    pricing = entry.get("pricing", {})
                    if not isinstance(identifier, str) or len(identifier) > 160 or not identifier.endswith(":free") or any(c.isspace() for c in identifier):
                        continue
                    if not isinstance(parameters, list) or not {"tools", "tool_choice"}.issubset(parameters):
                        continue
                    try:
                        if not isinstance(pricing, dict) or any(Decimal(str(pricing[k])) != 0 for k in ("prompt", "completion")):
                            continue
                    except (InvalidOperation, KeyError, TypeError):
                        continue
                    label = entry.get("name", identifier)
                    names[identifier] = label[:120] if isinstance(label, str) else identifier
                result = {"models": list(names), "names": names, "verified": True,
                          "code": "OK" if names else "NO_PERMITTED_MODELS",
                          "message": "Models allowed by this API key; provider capacity can still vary." if names else "No free tool-capable models are permitted. Update this key's OpenRouter guardrails/provider settings."}
                ttl = 60
            except Exception as error:
                expected = isinstance(error, AppError) and error.code in {"MODEL_AUTH_ERROR", "MODEL_CATALOG_UNAVAILABLE"}
                code = error.code if expected else "MODEL_CATALOG_UNAVAILABLE"
                message = str(error) if expected else "Could not verify permitted free models. Please retry shortly."
                result = {"models": [], "names": {}, "verified": False, "code": code, "message": message}
                ttl = 15
            self.cached, self.expires, self.fingerprint = result, stamp + ttl, fingerprint
            return result
