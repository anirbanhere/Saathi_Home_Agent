import pytest
from saathi.policy import Policy
from saathi.contracts import Action
from saathi.state import check_transition


@pytest.mark.parametrize(
    "tool,action,mock,approved",
    [
        ("payments.transfer", Action.PAY, True, True),
        ("appointments.book", Action.BOOK, False, True),
        ("appointments.book", Action.BOOK, True, False),
        ("appointments.search", Action.ORDER, True, True),
    ],
)
def test_model_cannot_grant_capabilities_or_approval(tool, action, mock, approved):
    with pytest.raises(ValueError):
        Policy().check(tool, action, mock=mock, approved=approved)


@pytest.mark.parametrize(
    "previous,following",
    [
        ("PLANNED", "COMPLETED"),
        ("CANCELLED", "APPROVED"),
        ("RECONCILIATION_REQUIRED", "COMMITTING"),
        ("COMPLETED", "COMMITTING"),
    ],
)
def test_illegal_state_transition_and_uncertain_replay_denied(previous, following):
    with pytest.raises(ValueError):
        check_transition(previous, following)
