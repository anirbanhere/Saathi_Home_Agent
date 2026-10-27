# Research and handoff usability verification

27 October 2026. Scope: current web UI, synthetic anonymous workspaces. This is targeted browser verification, not a full accessibility certification or Indic-language evaluation.

## Reproduced defects and fixes

On website revision `home-agents-00009-xhz`, discarding a handoff updated history while leaving its original result card actionable. Focus became BODY. Result panels now render their existing task from refreshed canonical state. Cancelled drafts lose their provider continuation link, and task actions recover focus to the corresponding control or named task card when their trigger disappears. Focus on another surviving control is left alone.

Research uses a separate atomic live status line instead of replacing saved sources with a progress paragraph. Result-panel source disclosures retain their open state across refreshes. Transport errors remain visible inline; task/model errors retain the saved evidence and explicit Needs details state. No new inference probes, polling, browser permissions, transaction execution or persistence schema were introduced.

## Reproduce locally

```text
python -m pip install -r requirements-hosted.txt
python tests/ui_fixture_server.py
```

Open `http://127.0.0.1:8766` in a fresh browser context. This loopback-only harness uses temporary synthetic visitor state, a synthetic model catalogue, local page observations and deliberate model capacity failures. It replaces provider credentials/config in process; it does not load `.env` or send provider requests. Stop it with Ctrl+C. The GCP source allowlist excludes tests and this harness.

In Activity, use `https://example.com/research` for an observed page and `https://example.com/blocked` for an HTTP403/Needs details page. AI research inspects once and then pauses with a synthetic RATE_LIMITED error. These observations are fixtures, not actual website/flight data. Save a food draft with a public provider homepage and demo details; discard from either its result card or history.

## Observed browser evidence

| Scenario | Observed result |
| --- | --- |
| Save/discard draft | Result and history both Cancelled; result has no link/discard action; focus returns to named Cancelled article |
| Keyboard source expansion | Tab reaches source link with `noopener noreferrer`; source text stays ordinary text |
| Adversarial source text | Literal `<script>…</script>` is visible; zero script elements were created |
| Research provider failure | Needs details and RATE_LIMITED trace; existing page retained; no Completed/live-flight claim |
| Keyboard resume | Continue research preserves expanded result source and returns focus to its refreshed control |
| Keyboard cancellation | Card becomes Cancelled, no Continue/Cancel actions remain, focus returns to article |
| Reload/resume | Tasks and pages survive reload; research can resume from history; displayed cancellation/status line agrees |
| Mobile visual check | Expanded source/history inspected in a screenshot; content fits without page overflow |
| Existing live website | Direct Python.org inspection succeeded through private worker before this UI update; no model-summary claim |

Verified Activity geometry using Chrome device emulation and DOM reads, after selecting Activity at each size (emulation changes can reload the document):

| Actual `innerWidth` | Document client width | Document scroll width |
| --- | --- | --- |
| 390 | 390 | 390 |
| 768 | 753 | 753 |
| 1440 | 1425 | 1425 |

The15px difference on larger viewports is the vertical scrollbar. No whole-page horizontal overflow was observed. Latest fixture-page console check contained no warnings/errors. No automated axe/screen-reader audit, full Core Web Vitals profile, every-device coverage or live successful LLM research journey is claimed.

## Regression checks and deployment

Existing97 Python tests passed; JavaScript syntax, Python compilation and Git whitespace checks passed. Browser interactions above are manual tool-driven regression checks; the harness is reproducible test data, not an automated browser suite. Production rollout/build and actual post-deploy checks are recorded in [HANDOFF.md](../HANDOFF.md).
