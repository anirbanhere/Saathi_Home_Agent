# Home Agents GCP deployment target

Updated: 26 October 2026, Asia/Kolkata.

## Confirmed target

| Setting | Value |
| --- | --- |
| Project name | Sathi Home Agent |
| Project ID | `sathi-home-agent` |
| Project number | `59012364414` |
| Deployment region | `us-central1` (US Central), selected by the user |
| VM zone | Not selected; choose an available zone in this region at provisioning |
| Environment | Demo |

The target is recorded in `../deploy/gcp/target.json`. This is deployment metadata, not a runtime configuration loader. No deployment scripts consume it yet. It contains no credentials. Regional application resources, the media bucket, and any eligible speech service should use this region unless a service's availability requires a separately recorded choice.

## Read-only verification

The installed Google Cloud CLI has an active login. Successful read-only checks confirmed:

- Project lifecycle: `ACTIVE`.
- Billing is enabled for this project. This does not establish the remaining credit balance, credit eligibility, or expiry.
- Cloud Storage, Logging, Monitoring, and Service Usage APIs are enabled.
- At the original preflight, Compute Engine, Secret Manager, Artifact Registry, Cloud Run, and Cloud Tasks APIs were absent. Cloud Run, Cloud Build, Artifact Registry and Secret Manager have since been enabled for the website deployment.

No project-wide CLI defaults were changed and no service-account keys were exported. Website resources and narrowly scoped runtime/build permissions have since been created; see `hosted-deployment.md` for the current inventory. Region selection here records the target; GCP projects do not become confined to a single region through this file.

## Next deployment preparation

1. Check credit balance/expiry and configure appropriate billing controls in the billing account. Inspect quotas and current regional prices before choosing a VM or GPU.
2. The user prioritized the public website before the owned clinic calendar. The website's anonymous visitor boundary and persistent kitchen/sandbox workflows are deployed; the clinic remains future work.
3. Prepare the pinned container runtime, persistent storage, private media, restricted service identity, HTTPS ingress, and backup/restore procedure.
4. Cloud Run is selected for this website. The VM deployment is a future option for a continuous WhatsApp worker; Compute Engine and Cloud Tasks are not required for the current site.
5. Deploy and verify a text booking first, then connect real model inference, speech, and the chosen WhatsApp route. Keep the clinic labeled as a demo.

The original localhost server remains local. A separate Flask/Gunicorn boundary serves the GCP site. The published Sites edition still uses browser-local state and is separate from the GCP website.
