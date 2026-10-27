# Saathi Phase0: vendor feasibility and launch gates

Research date:27 October2026. Primary documentation establishes interface availability, not our account access, legal eligibility or end-to-end success. No vendor account was paired, live call made or purchase attempted. Source document claims are not automatically execution instructions.

| Area | Primary evidence and implementation implication | Current gate |
| --- | --- | --- |
| WhatsApp | [Messaging policy](https://whatsappbusiness.com/policy/) retrieved (dated23 September2026). [Business terms](https://www.whatsapp.com/legal/business-solution-terms) redirected to blocked login; exact latest AI/country wording could not be independently verified. PRD flags material risk | Production eligibility false; authoritative offering-specific review and permitted test account absent. No public channel |
| Hermes | [Cloud API docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud) describe a dedicated business-number/HTTPS gateway. Treat current template behavior as version-dependent | Optional; no new Hermes runtime session. Not a WhatsApp prerequisite or policy workaround |
| Sarvam STT | [REST contract](https://docs.sarvam.ai/api-reference/speech-to-text/transcribe): multipart audio, subscription-key header, transcript/language. Provider exposes language probability separately from transcription accuracy | API contract spike and injected-transport tests only. No credential-backed Hindi/Tamil/English ASR quality result |
| Sarvam TTS | [REST contract](https://docs.sarvam.ai/api-reference/text-to-speech/convert): text/language/model/voice and base64 audio | Explicit model/voice config; disabled live calls until access/consent/cost approved |
| ElevenLabs STT | [Create transcript](https://elevenlabs.io/docs/api-reference/speech-to-text/convert): multipart file/model, API-key header, transcript/language. Retention options depend on account terms | Contract-only; no key/live test. Do not promise account-wide zero retention |
| ElevenLabs TTS | [Convert](https://elevenlabs.io/docs/api-reference/text-to-speech/convert): voice-specific endpoint and configured model/output format | Contract-only; no voice permission/account/quality evidence |
| Swiggy MCP | [Authentication](https://mcp.swiggy.com/builders/docs/start/authenticate/) uses OAuth2.1/PKCE. [Access](https://mcp.swiggy.com/builders/docs/operate/access/) describes reviewed allowlisting and local stub/staging development | No OAuth application/redirect approval. No checkout implementation/execution in Phase1 |
| Exotel | [AgentStream](https://developer.exotel.com/docs/agentstream/connect-voice-ai) documents outbound call setup and audio streaming | No approved account/recipient/compliance clearance. No test call executed; later mock only |
| IRCTC | [Published B2B norms](https://contents.irctc.co.in/en/NormsforB2B.pdf) describe partner eligibility/agreement requirements; document age/current applicability needs IRCTC confirmation | No authorized ticketing partner. No ticket scraping, CAPTCHA bypass or issue/PNR claims |

## Threat boundaries for Phase1

Browser/channel input, transcripts, model plans, tool results and approval requests are untrusted. A server-side session maps to one mock principal; request/model user IDs cannot change ownership. Typed schemas forbid extra fields and arbitrary tool names. Preview hashes bind actor/task/version/arguments/expiry; persisted approval decisions and unique operation keys prevent replay. SQL/outbox are authoritative; Redis failure cannot create an extra booking. Logs contain event IDs/codes/timings, not transcripts, credentials or internal reasoning.

Live flags default false and Phase1's factory refuses live execution even if a flag is flipped. Future enablement needs separate reviewed adapters, grants, account access, eligibility and meaningful provider/receipt tests. Local mock data is not appropriate for actual clinical/financial information.
