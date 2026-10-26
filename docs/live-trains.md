# Train running-status integration

Provider: RailRadar's documented authenticated REST endpoint, `GET https://api.railradar.in/v1/trains/{number}/live?date=YYYY-MM-DD&haltsOnly=true`.

## Setup and use

Use a separate RailRadar-issued key, not the LLM credential. Local `.env` is a setup reference; the app reads process environment. Production selects `HOME_AGENT_TRAIN_PROVIDER=railradar` in `deploy/gcp/env.yaml` and mounts `RAILRADAR_API_KEY` from Secret Manager secret `home-agents-railradar-key`. Keep the existing OpenRouter secret reference when updating the service.

The website's Activity form calls the same `train_status` tool directly. It does not require OpenRouter to be available. The AI tool description also supports this provider; it must observe the tool before making any location/delay claim. Enter the journey start date at the train's origin, especially for overnight services. Future dates cannot have running reports.

Without a selected live provider, local development retains explicit fixtures. Once RailRadar is selected, missing credentials or provider errors produce clear failures; they never substitute sample data.

## Data and limits

The adapter validates train/date identity, bounds external response sizes/fields, stops redirects, and never logs keys or raw provider output. It retains the provider update time separately from the fetch time. Reports older than 15 minutes are labeled stale. Missing/future timestamps, estimated position, or absent live flags do not qualify for a live badge. A completed service can naturally have an old final report. Position is the provider's latest reported location, not guaranteed GPS.

Only bounded normalized fields are passed to the agent/UI; provider data remains untrusted evidence. Status and concise summaries support the five application languages, while train/station names retain the provider spelling. Language coverage is not a fluent-speaker evaluation.

Responses are cached for two minutes per train/date/key, with a 32-entry process-local limit. A five-new-fetches/minute process limiter reduces abuse. These are not durable account quotas; restarts reset the cache/limiter. RailRadar advertises a 100-request/month free sandbox allowance; actual account entitlement and data freshness must be checked. No paid upgrade is selected automatically. [Provider overview](https://railradar.in/docs), [live endpoint contract](https://railradar.in/docs/live-train-status).

## Evidence and rollout

- 62 automated Python tests passed, including normalized fields, stale/estimated/missing/future timestamps, cache freshness, record mismatch, no fixture fallback, missing key/future date, and direct hosted lookup without an LLM. Synthetic tests do not count as live feed verification.
- Actual authenticated provider calls succeeded for train 12069 (completed journey, older update correctly labeled stale) and 12627 (running, recent provider report). The credential was streamed into Secret Manager without making an extra plaintext copy.
- Deployed revision `home-agents-00005-kng`, image build `f5de38ad-61e4-4c1c-9664-9590cf4cdcc2`. The public tool returned a recent 12627 running report with source/update times and persisted it to visitor task history without an LLM call. The browser form loaded with the correct India-time date and provider configuration.
- CI passed: https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40347816704 . The earlier LLM provider access/rate-limit problem is independent of this direct railway lookup.
