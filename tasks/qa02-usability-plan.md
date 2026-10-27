# QA-02: research and handoff usability

27 October 2026. Scope: existing anonymous web demo; synthetic inputs only.

## Reproduced failures before editing

On revision `home-agents-00009-xhz`, actual emulated viewport 390×844:

1. Activity → save a food draft using `https://www.swiggy.com` and synthetic details.
2. Activate Discard draft in the result above the form.
3. History correctly says Cancelled, but the original result still says Needs details and retains Discard draft.
4. Keyboard focus becomes BODY after the button is removed/disabled.

Direct Python.org inspection completed through the private browser; actual viewport and document width both390px. This is page inspection evidence, not a successful AI research answer.

## Intended change and acceptance

- Re-render already displayed result cards from canonical refreshed tasks, including cancellation from either history or the result panel. Preserve open source/details disclosures.
- Recover keyboard focus to the corresponding refreshed control or task card when a task action removes its trigger. Do not steal focus if the user moved to another control while waiting.
- Stop offering a provider continuation link on a cancelled draft.
- Keep research sources visible while a step runs, announce progress separately, and display recoverable errors inline. No extra polling/model requests.
- Verify source expansion, inspect/reload, resume/cancel, needs-input, sandbox distinctions, and viewport overflow at actual390/768/1440px. Distinguish synthetic provider-error checks from live inference evidence.
- Existing Python suite and JS syntax must pass; record runtime/browser evidence and any remaining limits in HANDOFF.md.
