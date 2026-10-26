# Proposed implementation checklist

Historical checklist: use [docs/backlog.md](../docs/backlog.md) and [docs/sprint-plan.md](../docs/sprint-plan.md) for current task selection. Checked/unchecked items below retain the original prototype scope, not the latest public release state.

Status: Local implementation completed for bounded offline workflows; live integration and submission items remain pending. See ../docs/implementation-status.md. File paths below were proposed before implementation; actual code is in home_agent/ and web/.
Each task should remain within roughly five implementation files; split any larger task before coding. Establish executable dev/test commands in Task 2 rather than inventing successful commands now.

## 1. Validate external dependencies
- Acceptance: Record final rules/submission requirements when accessible, hardware, WhatsApp connection route, and train-provider availability. Acceptance already confirmed; Meta access remains pending.
- Verify: Actual gateway pairing/message test and provider sample request; record live/sandbox status. Do not treat documentation review as a passed connection test.
- Dependencies: None.
- Files: docs/integration-checks.md, docs/hackathon-demo-spec.md.

## 2. Establish a runnable service and task store
- Acceptance: Normalize a text message, persist task state/preferences, restart, and retrieve the task. Document actual setup and test commands.
- Verify: Focused persistence test and one manual restart round trip.
- Dependencies: Task 1 resource findings.
- Files: pyproject.toml, README.md, app/main.py, app/storage/tasks.py, tests/test_tasks.py.

## 3. Complete the text train-status path
- Acceptance: Request missing train/date details, query the selected provider adapter, and return source/time-stamped data. Fixtures are explicitly labeled.
- Verify: Successful lookup, missing-field follow-up, and provider failure through normalized message input.
- Dependencies: Tasks 1–2.
- Files: app/tools/travel.py, app/agent/task_flow.py, tests/test_travel.py, demo/train_fixture.json.

### Checkpoint A
- [ ] Real WhatsApp connectivity is established or its blocker is documented.
- [ ] Text task persists and returns an actual provider/fixture result with the correct label.

## 4. Connect actual Hermes/Muse tool calling
- Acceptance: Muse requests the travel tool through Hermes, consumes the result, and handles a follow-up without losing task context. Pin versions verified in the integration.
- Verify: Actual model calls and tool traces; repeat a follow-up in each target language. Keep fixture results separate.
- Dependencies: Task 3 and Meta API credentials.
- Files: app/agent/runtime.py, app/agent/settings.py, tests/test_tool_contract.py, docs/integration-checks.md.

## 5. Deliver one WhatsApp voice round trip
- Acceptance: Decode incoming audio, transcribe with a selected Indic model, execute the task, and send a same-language spoken result.
- Verify: Actual phone voice message through the full pipeline; measure latency and confirm names/numbers manually.
- Dependencies: Task 4, WhatsApp connection, and speech resources.
- Files: app/gateway/whatsapp.py, app/speech/transcribe.py, app/speech/synthesize.py, tests/test_audio_formats.py.

## 6. Validate all four languages
- Acceptance: At least 10 representative cases per language cover voice/text, code mixing, missing fields, and critical identifiers. Record actual completion rates and failures.
- Verify: Run the recorded evaluation against real models; obtain fluent-speaker review where available.
- Dependencies: Task 5. Case collection can begin earlier.
- Files: evals/cases.jsonl, evals/run.py, evals/results.md.

## 7. Deliver sandbox bill payment
- Acceptance: Fetch bill, show biller/amount, persist approval, execute once, and check tool-backed status. Timeout leaves an uncertain outcome pending verification.
- Verify: Missing approval cannot execute; duplicate delivery does not double-pay; unknown result triggers a status check. Every receipt says sandbox.
- Dependencies: Tasks 2 and 4.
- Files: app/tools/billing.py, app/agent/approvals.py, app/storage/operations.py, tests/test_billing.py, demo/bills.json.

## 8. Add bounded ticket-booking sandbox
- Acceptance: Collect itinerary/passengers, show an option/fare, approve, execute the sandbox, and retrieve the booking result. Clearly distinguish sandbox reference from a real PNR.
- Verify: Correct/date ambiguity, cancellation before approval, duplicate execution, and service failure.
- Dependencies: Task 7 execution infrastructure.
- Files: app/tools/booking.py, tests/test_booking.py, demo/booking_options.json.

### Checkpoint B
- [ ] Agent 3 works with actual Muse and Indic speech in all four languages, with measured results.
- [ ] Transaction outcomes require approval and come from the tool; retries do not duplicate operations.

## 9. Deliver grocery-bill inventory ingestion
- Acceptance: Read items/quantities from a bill image, allow uncertain fields to be corrected, and persist purchase events once per bill.
- Verify: Inspect actual image extraction; reprocess the same bill and correct a quantity without duplicating stock.
- Dependencies: Tasks 2 and 4.
- Files: app/tools/groceries.py, app/storage/inventory.py, tests/test_inventory.py, demo/sample_grocery_bill.png.

## 10. Deliver customized cooking instructions
- Acceptance: Process accessible evidence from a selected recipe video, apply a voice customization, compare against stored inventory, and produce instructions/missing items. Mark inferred quantities.
- Verify: Compare instructions and ingredient extraction with source evidence; change inventory/customization and verify relevant changes in output.
- Dependencies: Tasks 5 and 9, accessible recipe evidence.
- Files: app/tools/recipes.py, app/tools/cooking.py, tests/test_cooking.py, demo/recipe_source.md.

## 11. Record meal consumption and suggest a dish
- Acceptance: Meal completion creates estimated consumption events and history; corrections are possible. Suggestions use current stock/history and do not themselves deduct inventory.
- Verify: Duplicate completion does not double-deduct; corrected stock persists; suggestion leaves stock unchanged.
- Dependencies: Task 10.
- Files: app/tools/meals.py, app/storage/meal_history.py, tests/test_meals.py.

### Checkpoint C
- [ ] One full household loop works: grocery bill -> inventory -> customized recipe -> completed meal -> estimated stock update -> grounded suggestion.

## 12. Verify sender permissions and untrusted media handling
- Acceptance: Household roles limit tool access; external captions/receipt text cannot authorize transactions or reveal secrets.
- Verify: An unauthorized sender cannot execute tools; the cook cannot access personal bills; injected media instructions cannot change permissions.
- Dependencies: Tasks 5, 7, and 10.
- Files: app/agent/access.py, tests/test_access.py, tests/test_media_instructions.py.

## 13. Prepare and submit the demo
- Acceptance: Rehearsed recording matches working behavior; setup and evaluation results are documented; live/sandbox limitations and model roles are clear.
- Verify: Run documented setup on a clean environment, replay demo cases, inspect final event form/rules, and verify submission receipt. Submit only when authorized by the user.
- Dependencies: Checkpoints A–C and Task 12.
- Files: docs/demo-script.md, docs/limitations.md, README.md, evals/results.md, demo/reset.py.

### Final checkpoint
- [ ] No unverified live-service, language-accuracy, or performance claims.
- [ ] No secrets in repository or recording.
- [ ] Recording and required artifacts are ready before 4 November scope freeze.
- [ ] Successful submission is verified independently of local file completion.
