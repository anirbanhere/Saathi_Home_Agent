# Voice and WhatsApp implementation plan

Status: proposed. Current product has no paired WhatsApp transport and no hosted ASR/TTS service. Target languages are Tamil, Malayalam, Kannada, Hindi and English. The existing local JSON speech adapter is reusable contract evidence, not a working voice deployment.

## Deliver a web voice slice before depending on channel setup

1. Accept a bounded supported audio file through an authenticated/scoped application path. Validate real content/MIME, size, duration and ownership; do not trust filename extensions.
2. Normalize codecs in an isolated media component. Keep source reference, checksum, task/version and requested/detected locale.
3. Call a versioned ASR service with a private media reference or bounded audio payload. Preserve transcript plus uncertainty where available; the model/provider may not supply calibrated confidence, so do not invent it.
4. Show or read back critical fields: service/train numbers, dates/times, names, money, quantities, destination/address. Low confidence, ambiguity or conflicts require clarification before any write.
5. Route confirmed text through the same validated tools and task policy. Transcription itself does not authorize execution.
6. Generate a concise same-language response, preserve any receipt/source data and synthesize through TTS. Keep a text equivalent and an explicit retry path for speech failures.
7. Save task state separately from audio. Delete audio according to the implemented retention policy; do not keep recordings in source control or ordinary application logs.

Proposed initial retention: delete raw/normalized demo audio within 24h unless the user explicitly opts into a separately scoped evaluation collection; shorter deletion on request. This is a design target, not an existing lifecycle configuration. Validate and implement the actual policy before public audio collection.

## Existing versus proposed contracts

| Boundary | Existing local contract | Required hosted additions |
| --- | --- | --- |
| ASR | Request `audio_base64`, `mime_type`, `language`; response `text`, `language` | Principal/task scope, size/duration/codec validation, private storage/expiry, normalized errors, measured language quality |
| TTS | Request `text`, `language`; response `audio_base64`, `mime_type` | Same-language fidelity, bounded text/audio, timeout/retry, authorized access and text fallback |
| App ingress | Local `/api/speech/transcriptions` and `/api/speech/syntheses` | New hosted routes require explicit schemas and tests; they do not currently exist in `hosted.py` |
| Model handoff | Validated text message/tool loop | Trace transcript corrections and task version; speech retry cannot replay a completed tool |

Benchmark open-weight Indic ASR/TTS candidates before choosing models or hardware. Record exact weights/version/license, supported locales, transliteration/code-switching behavior, CPU/GPU memory, cold start, real-time factor, p50/p95 and recurring hosting cost. A licence/quality/hardware decision is an implementation prerequisite, not a reason to promise an untested model. Avoid always-on GPU allocation until measurements and available credits justify it.

## WhatsApp route decision

Evaluate an official webhook-based business route and a Hermes-supported bridge as separate alternatives. Verify current primary documentation, account/number eligibility, test recipients, voice media access, message-window/template restrictions, signature verification, session persistence, supported group behavior and acceptable-use constraints before selecting. Do not presume a consumer group with the cook is supported by the chosen route.

Record the selection in an ADR with actual evidence and a working direct-message test. Prefer a controlled direct-message demo before group features. A continuously connected bridge has different deployment/session requirements from a stateless webhook; keep it off the public website's anonymous console boundary.

No unsolicited message or account pairing is authorized just by this plan. Test against an explicitly approved recipient/number with the required human setup. Channel credentials stay in a private secret/session store; neither a QR/session file nor an OTP belongs in Git, logs, a prompt or a public screenshot.

## Channel pipeline and delivery

```text
verify inbound signature/session → resolve authenticated sender binding
→ deduplicate provider event/message → persist inbox record
→ enqueue task job → obtain and validate media
→ transcribe → clarify critical fields → plan/execute allowed tool
→ persist task/result + reply intent → outbox delivery
→ record provider acknowledgement / uncertain delivery / bounded retry
```

Return webhook acknowledgement only after the needed durable receipt is recorded; avoid holding it open through the whole speech/model journey. Design for duplicate/out-of-order events, provider timeouts, worker restart and revoked sender membership. At-least-once delivery is not exactly-once human receipt. Delivery ambiguity must not recreate an appointment, meal deduction or payment.

For clarification/approval, bind a reply to sender, conversation, task ID/version and exact active prompt. Two pending tasks, quoted old messages, a different group member or a delayed “yes” cannot authorize an unrelated action. Language and timezone preferences are revocable stored data, not implicit rules from a transcript.

## Four-language acceptance

Start with ten recorded tasks per Indian language and five English tasks, with permission to use the recordings. Include code switching, spoken numbers, relative dates, noise, named places and ambiguous requests. Obtain human reference transcripts and expected critical fields. Do not publish identifiable recordings without separate consent.

Measure transcription error and critical-field correctness separately from end-to-end task success. Proposed initial task target: at least 8/10 correct tool outcomes per Indian language, with every executed action matching the exact details confirmed by the user. This is a proposed gate, not a measured result. Report per-language failures; a pooled average cannot hide a weak locale.

Review response clarity/pronunciation with speakers. TTS failure should preserve the actual tool result and text response. ASR/model failure should preserve a recoverable task rather than creating a fake receipt. See [evaluation](testing-and-evaluation.md) for the complete evidence matrix.

Tickets: `VOICE-01` through `VOICE-03`, `WA-01` through `WA-03`, preceded by appropriate identity/job/media foundations.
