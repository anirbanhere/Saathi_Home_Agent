# Public Home Agent demo

Published URL: https://home-agent-indic-demo.glassyibex32.chatgpt.site

Sites confirmed deployment succeeded on 26 October 2026. Audience: public, as requested by the user; anyone with the link can visit.

## Deployment identity

- Project: `appgprj_6adf33efc720819194a96a1401c23c7f`
- Saved version: `appgprj_6adf33efc720819194a96a1401c23c7f~appgver_9e5dee09ae3481919df61484d361788b` (version 1)
- Deployment: `appgdep_6adf3615bc04819196eb3d0d1b7f3be3`
- Source commit: `8e7044b401a70b17ffa0c1849035302d628f2f7c`
- Source checkout: `sites/home-agent-demo/`, a separate managed Git repository with `.openai/hosting.json` declaring the exact project ID and `dist` static directory.

## What visitors can demonstrate

Four-language offline conversations and follow-ups; sample train lookups; sandbox bill payments and journey bookings with approval and receipts; grocery text ingestion; stock correction; curated cooking plans and estimated meal consumption.

Sites does not run the local Python/SQLite process. This publication ports the offline workflows to a browser-local JavaScript engine. Each visitor starts with synthetic stock and keeps their own messages, inventory, and task history in that browser's storage. Data is not shared across visitors or synchronized across devices. No local database, personal conversations, API credentials, or live connections were published.

Muse, Hermes, WhatsApp, actual Indic speech, video extraction, bill-image extraction and live provider integrations remain disconnected. The original Python prototype and its adapters remain available in the parent workspace.

## Verification

Thirteen Node tests passed for the public edition, covering four languages, isolated visitor state, replay protection, atomic stock changes, cancellation and sandbox approval. JavaScript syntax checks passed. A browser walkthrough verified a Malayalam bill request, review dialog, sandbox approval and saved receipt without console errors. The Sites native deployment result verified the production URL and succeeded state.

## Future updates

Reuse the existing project ID and source checkout. Obtain a fresh source write credential with Sites tools when needed, edit and test in the same checkout, then use the Sites source helper to push/package, save a version and deploy with the public-audience flow. Never copy credentials or the parent application's data directory into the Site.

`scripts/prepare-assets.py` inside the Site checkout can refresh the public UI/catalog from the Python prototype. It applies the browser transport and copy changes; `dist/demo-store.js` is maintained separately. Read the Sites skill before making hosting changes.
