# Honest local demonstration

This walkthrough demonstrates the offline prototype, not the finished Meta/WhatsApp product. Approximate narrative length: three minutes; this is a suggested presentation length, not a verified event requirement.

1. Open Assistant. Point out the offline/sample/sandbox banner. Explain the intended Hermes + Muse + Indic speech stack and show Connections to distinguish implemented adapters from live integrations.
2. Choose Tamil, Malayalam, Kannada, or Hindi. Ask for a train's status without the date, then supply `12627 2026-11-01`. Show the same-language follow-up and response. Explicitly say the train position is a local fixture.
3. Ask to pay the electricity bill for `DEMO-1042`. Show the amount before approval. Open Review & approve, inspect the sandbox warning, and approve. Show the persisted `SANDBOX-` receipt. No money moves.
4. Open Kitchen and add the default grocery lines with a unique bill reference. Submit the same reference again to show stock is not doubled.
5. Create a two-person tomato-rice plan with less chilli. Explain that the recipe is curated, steps are English, and quantities are estimates. Inspect ingredient availability.
6. Mark cooked and show stock and inventory history changing once. Open Activity and inspect the completed cooking plan.
7. Show a sandbox journey and cancellation, or an unsupported train fixture as the failure case. End with the actual remaining integrations: Meta credentials, Hermes/WhatsApp session, real Indic speech, source-video extraction, bill-image extraction, and live providers.

To rehearse with clean state, start a separate database and port instead of deleting the existing database:

```powershell
python -m home_agent --port 8766 --db data/rehearsal.sqlite3
```
