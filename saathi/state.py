"""Allowed task transitions; no client/model can set a status directly."""

TRANSITIONS = {
    "RECEIVED": {"UNDERSTANDING", "CANCELLED"},
    "UNDERSTANDING": {"CLARIFICATION_REQUIRED", "PLANNED", "REQUIRES_USER_ACTION"},
    "CLARIFICATION_REQUIRED": {"UNDERSTANDING", "CANCELLED"},
    "PLANNED": {"APPROVAL_PENDING", "CANCELLED"},
    "APPROVAL_PENDING": {
        "APPROVAL_PENDING",
        "APPROVED",
        "PLANNED",
        "REJECTED",
        "CANCELLED",
        "REQUIRES_USER_ACTION",
    },
    "APPROVED": {"COMMITTING"},
    "COMMITTING": {"VERIFYING", "RECONCILIATION_REQUIRED"},
    "RECONCILIATION_REQUIRED": {"VERIFYING"},
    "VERIFYING": {"COMPLETED"},
    "REQUIRES_USER_ACTION": {"CANCELLED"},
    "REJECTED": {"CANCELLED"},
    "CANCELLED": set(),
    "COMPLETED": set(),
    "EXPIRED": set(),
    "FAILED": set(),
}


def check_transition(previous, following):
    if following not in TRANSITIONS.get(previous, set()):
        raise ValueError("Invalid task state transition.")
