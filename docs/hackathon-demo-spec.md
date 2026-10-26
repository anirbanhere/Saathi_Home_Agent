# Home Agent: Meta hackathon demo specification

Current design update: [home-agents-redesign.md](home-agents-redesign.md) supersedes this document's workflow ordering and fixed-model assumptions. Appointment booking against an owned demo clinic calendar is now the hero workflow; all four original languages and all three domains remain in scope. This file preserves the earlier prototype specification.

Status: Local prototype implemented following user authorization. The full hackathon scope below remains a target; see implementation-status.md for completed and pending capabilities.
Updated: 26 October 2026, Asia/Kolkata.

## Objective

Build a personal assistant accessed through WhatsApp that understands Tamil, Malayalam, Kannada, and Hindi and completes bounded household tasks. Preserve all three requested capabilities: everyday tasks (Agent 3, first priority), cooking (Agent 1), and kitchen inventory (Agent 2).

Proposed pitch: "Speak your language. Get everyday things done."

The household is the initial user. The hackathon demo should show actual tool execution, persistent state, and replies in the requested language. Everyday-task execution is the main demonstration; cooking and inventory demonstrate reuse of the same foundation.

## Assumptions to validate

- Hosted Meta Muse inference is acceptable for this time-limited demo. Full local inference is not yet a user requirement.
- Use open-weight Indic speech services; evaluate the four languages before choosing checkpoints.
- Booking and payment use an explicitly labeled sandbox unless suitable provider credentials and access are already available.
- A dedicated WhatsApp test number is available. The unofficial personal bridge has account and reliability risks; the official business path does not automatically satisfy this personal/group use case.
- Hackathon acceptance is confirmed by the user. Meta Model API setup is deferred. Team size, hardware, and GPU budget are unknown.
- Proposed stack choices below are recommendations, not decisions already approved by the user.

## Event facts and unresolved rules

- Organizer: https://cerebralvalley.ai/e/meta-ai-developer-hackathon
- Meta event page: https://dev.meta.ai/events/global-hackathon
- Build period: 26 October–4 November 2026.
- Published submission deadline: 4 November, 9:00 p.m. ET = 5 November, 7:30 a.m. IST. Internal completion target: 4 November afternoon IST.
- Proposed theme: Build for Your World. Track depends on participant/team status; Indie is a candidate, not an assumption about eligibility.
- The event page lists creativity, technical ambition, and working implementation for Indie; technical execution and production robustness for Startup.
- Full official rules, exact submission fields, video duration, external framework eligibility, and checkpoint/provider restrictions have not been verified. The linked waiver returned only a loading page through the research tool. Do not present third-party summaries as confirmed rules.

## Demo scope

### Agent 3: vernacular everyday tasks

1. Accept voice notes and text in all four target languages. Include native-script text, Romanized text, and English code mixing in evaluation.
2. Extract intent and necessary fields, ask for missing information, and retain context across follow-up messages.
3. Implement one train-status lookup using an accessible provider. Display source and retrieval time. If live access is unavailable, label replay/fixture results explicitly; a fixture does not count as a live integration.
4. Implement a bill-fetch and payment workflow in a provider sandbox or explicitly labeled local simulator. Present biller and amount before execution, record approval, and return a sandbox receipt only after the tool reports success.
5. Represent ticket booking as a separate bounded workflow: collect itinerary, search, present option and fare, approve, execute, and check status. Include actual booking only if provider access is available in time; otherwise demonstrate and label the sandbox path.
6. Reply in the user's chosen language; provide a short spoken reply as well as text for the main demo.
7. Handle one deliberate failure: ambiguous date, missing station, or service timeout. Never claim a task completed from model-generated text alone.

### Agent 1: cooking

1. Use one selected YouTube cooking video with accessible source material. Record which evidence was actually processed: transcript, audio, and/or selected frames. A URL alone does not establish video access.
2. Extract ingredients and ordered cooking steps with source references; mark inferred quantities and missing details.
3. Apply a voice-note customization such as fewer chillies or a serving-count change.
4. Compare ingredients with inventory and produce a missing-ingredient list and short instructions in the cook's preferred language.
5. Offer a dish suggestion grounded in available ingredients and recorded meal history.

### Agent 2: inventory

1. Extract grocery items and quantities from one bill image and allow corrections before committing uncertain entries.
2. Store purchase additions and consumption deductions as separate events with source and timestamp.
3. Deduct estimated consumption only after meal completion is reported; preserve uncertainty and support corrections.
4. Reprocessing the same bill or meal must not duplicate inventory changes.

## Proposed architecture

WhatsApp adapter -> message normalization -> Indic speech transcription when needed -> Hermes Agent with hosted Muse -> typed domain tools -> persistent household/task database -> verified result -> reply in the chosen language -> optional Indic text-to-speech.

- One gateway and runtime with three bounded domain handlers; three independent infrastructure stacks are unnecessary for this demo.
- Hermes supplies orchestration. Muse handles language understanding, planning, and response composition. Explicit application code owns approval and task state.
- Current local service boundary: Python standard-library HTTP server and SQLite, with JSON adapters for external inference. The HTTP server binds only to loopback and is not a production deployment.
- Task states: needs_input, awaiting_approval, executing, succeeded, failed, unknown. An uncertain external result becomes unknown until checked.
- Use an operation key for retries and perform a provider status query before retrying a booking or payment with an uncertain outcome.
- Preserve original names and identifiers. Normalize dates, currency, and quantities separately from translating response text.
- Store each user's preferred language and script; language detection alone must not override an explicit preference.
- Authorize the household's sender IDs. A cook's access to cooking/inventory does not grant access to personal bills or travel records.
- Use a credential store/environment variables; models and transcripts never need payment PINs or raw secrets.
- Keep media content separate from tool instructions. Video captions and bill text must not change execution permissions.

## Model candidates and integration checks

- Muse: hosted Meta Model API; validate structured tool calling, tool results, follow-up turns, and the four languages through Hermes before committing to the integration.
- ASR: evaluate Indic-Transcribe against IndicConformer on the same recordings.
- TTS: evaluate Indic-Speak against IndicF5 for the four target languages.
- IndicConformer and IndicF5 model cards list MIT; newer Indic-Transcribe and Indic-Speak use Indic Open Model License terms and upstream dependencies. Verify the selected weights' actual license before distribution.
- Hermes documents Whisper-based voice transcription; an Indic ASR/TTS adapter is expected development work.
- The local application was verified on Python 3.14.5 with no third-party runtime packages. Pin external framework/model/checkpoint versions when those services are connected; no live provider combination has been validated yet.

## Proposed project structure

```text
docs/                  Specification, source notes, demo script
app/gateway/           WhatsApp and normalized message handling
app/speech/            Transcription and synthesis adapters
app/agent/             Hermes/Muse configuration and domain routing
app/tools/             Travel, billing, recipe, and inventory tools
app/storage/           Persistent tasks, inventory events, preferences
tests/                 Task-state, tool, authorization, and retry tests
evals/                 Four-language audio/text cases and results
demo/                  Labeled fixtures, reset instructions, recording
```

## Commands and code style

Implemented and verified commands:

```powershell
python -m home_agent
python -m unittest discover -s tests -v
python -m evals.run
python -m compileall -q home_agent
node --check web/app.js
```

The Python application needs no third-party runtime dependencies. Source lives in home_agent/ and web/; the app/ structure above remains the earlier proposed layout.

Use typed Python, snake_case functions, explicit domain results, and decimal/integer minor units for money. Example contract (illustrative only):

```python
def check_payment_status(operation_id: str) -> PaymentResult:
    ...
```

## Testing strategy and acceptance targets

- Assemble at least 10 representative utterances per language, covering voice and text, code mixing, follow-ups, and missing details. This is a small demo evaluation, not a broad language-quality claim.
- Report intent/field accuracy separately from end-to-end completion. Names, dates, station identifiers, and amounts are critical fields.
- Correctly complete at least 8 of 10 supported cases in each language using the appropriate live/sandbox tools; publish the actual counts and failures.
- Every tested payment/booking execution requires the applicable approval and returns tool-backed status. Duplicate inbound delivery and execution retries must not duplicate side effects.
- Show one successful persisted task after restart and one service failure without a fabricated success response.
- Show receipt ingestion -> inventory correction -> recipe ingredient check -> customized instructions -> confirmed meal -> estimated stock deduction.
- Have fluent speakers review the four-language demo samples where available; mark any language without human review.
- Measure response latency, tool duration, and model/speech costs on actual hardware. Make no unmeasured latency promises.
- Rehearse the actual WhatsApp path. A local fixture path is a separately labeled fallback, not proof that WhatsApp works.

## Boundaries

- Always: label live/sandbox/replayed data, persist execution state, check actual results, preserve correction history, keep credentials out of source control.
- Clarify before changing scope: spending real money, making real bookings, publishing externally, or replacing a requested capability with a simulation in the final product.
- Never: fabricate receipts or live train positions, imply perfect inventory knowledge, deduct stock from a recipe suggestion, or present unprocessed video content as observed.
- Demo exclusions: universal task execution, every travel/biller integration, guaranteed support for arbitrary WhatsApp groups, and production-grade autonomous payments.

## Suggested delivery windows

These are provisional scope windows, not estimates based on known team capacity.

- 26–27 October: confirm event access; test Muse/Hermes tool calling, one voice round trip, WhatsApp connectivity, and service access.
- 28–29 October: complete the main Agent 3 path with persistence, clarification, approval, and a verified sandbox result.
- 30 October: complete all four language paths and collect initial evaluation results.
- 31 October–1 November: connect grocery-bill ingestion, inventory events, and the selected cooking-video workflow.
- 2 November: test failure/retry behavior, sender permissions, and multilingual field accuracy.
- 3 November: rehearse and record the demo; prepare reproducible setup and limitations.
- 4 November: freeze scope, check final rules/form requirements, submit early, and verify submission receipt.

## Next unresolved dependency

Participant acceptance is confirmed. Confirm available hardware and establish Meta API access early enough to validate Hermes/Muse tool calling; target 28 October or earlier. Until then, implement deterministic tools and explicitly labeled model fixtures. The first integrated milestone is one genuine four-part round trip: WhatsApp voice input -> Indic transcription -> Hermes/Muse tool call -> same-language spoken result. See tasks/plan.md and tasks/todo.md for the proposed execution sequence.

## Technical sources

- https://hermes-agent.nousresearch.com/docs/reference/faq
- https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp
- https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud
- https://dev.meta.ai/docs/overview
- https://dev.meta.ai/docs/muse-spark-open
- https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual
- https://huggingface.co/ai4bharat/IndicF5
- https://huggingface.co/bodhan-ai/indic-transcribe-core
- https://huggingface.co/bodhan-ai/indic-speak
