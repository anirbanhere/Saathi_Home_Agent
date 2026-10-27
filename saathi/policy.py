import hashlib
import hmac
import json
from .contracts import Action, BookingIntent, ToolManifest


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode()).hexdigest()


class Policy:
    allowed = {
        "appointments.search": Action.READ,
        "appointments.prepare": Action.DRAFT,
        "appointments.book": Action.BOOK,
        "reminders.draft": Action.DRAFT,
    }

    def check(self, tool, action, *, mock, approved=False):
        if not mock or tool not in self.allowed or self.allowed[tool] != action:
            raise ValueError("Capability/provider/action is not granted in Phase1.")
        if action == Action.BOOK and not approved:
            raise ValueError("A current server-validated human approval is required.")

    def registry(self):
        return [
            ToolManifest(
                name=name,
                action=action,
                input_schema=BookingIntent.model_json_schema(),
                output_schema={"type": "object", "required": ["mock"]},
            ).model_dump(mode="json")
            for name, action in self.allowed.items()
        ]


def verify_token(raw, expected_hash):
    return isinstance(raw, str) and hmac.compare_digest(
        hashlib.sha256(raw.encode()).hexdigest(), expected_hash
    )
