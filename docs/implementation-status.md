# Implementation status — 26 October 2026

## Working local prototype

| Area | Implemented | Verification |
| --- | --- | --- |
| Conversation | Offline phrase routing, missing-field follow-ups, language templates, restart persistence, duplicate message handling | Workflow tests and actual browser requests |
| Agent 3 | Train fixtures, sandbox bill preview/approval/receipt, sandbox booking preview/approval/cancellation | HTTP/workflow tests; bill approved in browser |
| Agent 2 | Reviewed grocery CSV, unit conversion, atomic imports, replay protection, corrections, event history | Workflow tests; browser grocery import |
| Agent 1 | Three curated recipes, scaled servings, lower chilli quantities, stock comparison, missing items, dish suggestions and meal consumption | Workflow tests; browser cooking-plan completion |
| Hermes | Stdio MCP adapter and fixed owner/cook roles; shared database; approvals excluded from tools | Protocol tests and actual subprocess from a different working directory |
| Muse | Direct API adapter, tool schemas, response validation, bounded output and explicit provider failures | Simulated provider-boundary tests, not a live Meta call |
| Speech | Opt-in ASR/TTS JSON adapter, audio file input, transcript review and spoken-reply control when configured | Code and contract checks; actual inference not connected |
| Browser | Assistant, Kitchen, Activity, Connections; responsive controls and dialogs | Actual Chrome walkthrough and accessibility audits |

All transaction outcomes in this build are local simulations. Recipe instructions are English. Introductory/status templates support Tamil, Malayalam, Kannada and Hindi; this does not establish general language fluency.

## Verification evidence

- `python -m unittest discover -s tests -v`: **31 tests passed**. Includes concurrency, replay conflicts, stock rollback, permissions, model/speech output validation, real MCP subprocess, cross-origin requests, unexpected Host headers and malformed HTTP input.
- `python -m evals.run`: **40/40 synthetic offline text-routing cases passed**, 10 per target language. No Muse, speech, or fluent-speaker evaluation was performed. Case-level results are generated under data/.
- `python -m compileall -q home_agent` and `node --check web/app.js`: passed.
- Browser demonstration: sample train lookup; Tamil bill request, approval dialog and sandbox receipt; grocery-text import; less-spicy tomato-rice plan; meal completion and corresponding stock deductions.
- Chrome Lighthouse snapshot audits reported 100 accessibility, 100 best practices, 100 SEO and 100 agentic browsing on the tested desktop and mobile Assistant states. These are snapshot audits, not a production certification or performance measurement.
- Layout checked at 1440px desktop and a 320px emulated mobile viewport; the final 320px Assistant has no horizontal page overflow. Other target sizes and workflow states remain subject to further device testing.
- Browser console had no errors/warnings in the checked state.

## Remaining connections

1. Set up Meta Model API access and validate actual Muse function calls, tool results, four-language understanding and follow-ups.
2. Connect the MCP server to a chosen Hermes profile, then test the complete Hermes/Muse loop. Existing personal Hermes settings have not been changed.
3. Choose and test the WhatsApp path on a dedicated number, including sender authorization and cook-group behavior. No account was paired and no external messages were sent.
4. Deploy actual Indic ASR/TTS weights on suitable hardware and evaluate voice recordings, mixed language, names, dates, pronunciation and latency.
5. Add source-video/transcript and grocery-image extraction. The current recipe source is explicitly curated and groceries are reviewed text.
6. Integrate approved live train, booking and payment providers as available. Current adapters deliberately do not perform real transactions.
7. Verify complete official event rules and submission fields, create the actual recording and submit with the user's authorization. No submission has been made.

## Scope decisions

- Standard-library local server rather than a framework dependency for the initial runnable demo. Production deployment requires an appropriate server/authentication design.
- Browser console is a trusted single-owner local interface. MCP roles are fixed in configuration; a cook cannot read personal tasks or approve transactions. This is not a public multi-user access system.
- Read-only/preview tools are exposed to the model. Human-controlled state transitions stay in application code.
- No external API keys, user accounts, service purchases or model downloads are necessary for the current offline experience.
