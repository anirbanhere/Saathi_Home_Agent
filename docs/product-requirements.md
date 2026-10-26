# Product requirements

Status: confirmed direction plus explicitly proposed release criteria. Baseline: 26 October 2026. This document does not authorize real transactions or third-party messages.

## Product and users

Home Agents helps an Indian household complete ordinary tasks through short conversations, primarily WhatsApp voice over time. Agent3 (everyday assistance) is first priority. Agent1 (cooking) and Agent2 (inventory) use the same identity, task and tool foundation; they do not require three separately deployed autonomous agents.

Primary users are a household owner who requests tasks and approves actions, a cook who needs practical dish instructions and stock visibility, and household members with future explicitly assigned access. A hackathon viewer should be able to understand the real demonstration without private accounts or ambiguous simulation labels.

Target languages are Tamil (`ta`), Malayalam (`ml`), Kannada (`kn`), Hindi (`hi`) and English (`en`), including code switching and spoken numerals. A language selector or template translation alone is not multilingual voice acceptance.

## Confirmed decisions

- Keep model choice interchangeable. Initial hosted provider is OpenRouter free inference; Meta access comes later. Preserve zero-cost model routing unless the human explicitly changes that policy.
- Use GCP project `sathi-home-agent`, region `us-central1`. Reported INR 15,000 resources are not a verified remaining balance or spending authorization for unrelated services.
- Public website is the immediate executable demo. WhatsApp voice remains the primary long-term channel.
- Use an owned, clearly labeled demo clinic calendar if building appointments; do not imply a real clinic agreement.
- Combine reliable APIs, isolated public browsing and account/human handoffs. Do not ask each end user for a developer key per task.
- Nous setup/model testing was skipped by the human. It is not a prerequisite for the roadmap.

## Required journeys and acceptance

| Journey | Input and desired behavior | Acceptance evidence | Current gap |
| --- | --- | --- | --- |
| Everyday public information | Ask for a train or public fact; collect exact identifiers/date; use provider/browser evidence | Source, freshness, exact requested service/date, truthful unsupported outcome | Live model capacity; wider sources vary |
| Voice task | Receive voice, transcribe, clarify a critical field, execute an allowed tool, respond in chosen language | Real recorded input and actual task outcome, independently reviewed language response | ASR/TTS/channel not connected |
| Demo appointment | Find owned clinic/service slots; select; confirm exact details; book once; retrieve/cancel | Durable owned calendar, one booking per slot, restart/duplicate/concurrency tests | Entire workflow planned |
| Bill/food assistance | Prepare details; show final provider data; obtain scoped confirmation where execution exists | Present release: labeled draft/manual handoff. Future: actual provider receipt and reconciliation | Real execution intentionally absent |
| Recipe from source + custom voice | Extract accessible recipe evidence, apply preferences, check stock, give simple steps | Identify processed source, quantities/estimates, missing ingredients and readable steps | Video extraction and voice customizations unconnected |
| Stock from groceries/meal | Review list/receipt extraction, import once, consume only after meal confirmation, correct mistakes | Original reference, normalized units, estimate labels, append-only changes and repeat safety | Reviewed CSV works; OCR and household sharing planned |
| Cross-domain suggestion | Use current inventory and recent completed meals to suggest feasible dishes | Explain availability/missing items, do not silently deduct stock | Curated subset implemented |

Clarifications must preserve exact names, times, amounts and identifiers. Resolve relative dates in the user's intended timezone; retain canonical timestamps separately. Never infer a ticket/bill number or delivery address because a language model supplied one.

## Release levels

**Current public prototype:** reliable direct tools and public page inspection, scoped anonymous persistence, explicit sandbox/draft labels, observable failures. Model-backed reasoning remains capacity-dependent.

**Demo-ready target:** one real free-model/tool journey, one evidenced voice task in a declared tested language, repeat/restart safety, clear source/transaction labels, and a reproducible recording. Four-language coverage remains a measured target; disclose any untested locale rather than claiming all four.

**Private household beta target:** verified account/channel ownership, revocable memberships, durable inbox/jobs/outbox, four-language voice evaluation, data deletion and operational monitoring. Public information and owned demo appointments may run here; financial execution has an additional independent gate.

**Transactional product target:** provider-supported account access, exact-action approval, durable operation ledger, uncertain-result reconciliation, verified receipt/cancellation and explicit human authorization to activate each real integration.

## Proposed non-functional acceptance

| Area | Acceptance requirement |
| --- | --- |
| Correctness | No success receipt without verified execution; denied or uncertain providers remain explicit |
| Ownership | Every stored task/media/approval is scoped to the authenticated principal or current visitor; a guessed ID grants nothing |
| Recoverability | Duplicate ingress/approval/job delivery cannot duplicate a local owned booking or stock event; uncertain external operations reconcile before retry |
| Usability | One focused clarification; short spoken response plus readable details; critical fields read back before commit |
| Observability | Capture task/operation IDs, phase latency and normalized error codes, without raw secrets/audio/transcripts by default |
| Latency | Measure ASR, planning, tool, TTS and overall p50/p95 before setting an SLA. Initial demo investigation threshold: journeys over 60s need a visible progress/failure path, not an unmeasured speed promise |
| Cost | Model routes remain verified free. Hosting/media/speech are metered separately; budget alerts are not hard spend caps |
| Accessibility | Keyboard, visible focus, labeled fields, progress announcements and narrow-screen checks for new UI |

## Scope cuts

No universal website automation claim, CAPTCHA bypass, implicit payment authority, unrestricted computer control, always-on GPU, Kubernetes requirement, hardware device, unrestricted family-group access, or unverified Meta/hackathon-compliance claim. Preferences and personal memory require a product storage/consent mechanism; repository Markdown is engineering context only.

Use [roadmap](roadmap.md) for delivery order and [backlog](backlog.md) for independently verifiable work.
