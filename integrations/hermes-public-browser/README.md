# Restricted Hermes public browser bridge

This is a plugin using Hermes's documented `register(ctx)` contract, checked against upstream source commit `d49e2ebbaed42718659c13f82c04cde7d8ab10bd`. Registration, validation and handler tests pass in Home Agents. **A real Hermes model session has not been run; the website currently uses its application-owned loop.**

The inspected upstream requires its PM-managed Python 3.14 source environment. Do not install an unrelated package named Hermes into this application's Python 3.12 environment. Follow [the upstream source installation/library guide](https://hermes-agent.nousresearch.com/docs/guides/python-library).

To connect in a separate, supported Hermes environment:

1. Install the contents of this directory under `$HERMES_HOME/plugins/saathi-public-browser/` and enable `saathi-public-browser`. Gateway sessions do not load a project-local plugin automatically. See [Hermes plugins](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins).
2. Make this repository's `home_agent` package importable in that environment (`PYTHONPATH` pointing at the checkout), and install the client dependencies from `requirements-hosted.txt` in that separate environment.
3. Set `HOME_AGENT_BROWSER_WORKER_URL` to the private Cloud Run worker URL. Use a workload identity authorized with `roles/run.invoker` on that one service. No worker API key or exported service-account JSON key is needed. A normal local user ADC is not necessarily sufficient to mint the required service identity token; prefer a dedicated GCP runner or explicitly configured authorized impersonation.
4. Expose only the `saathi_public_browser` toolset in the dedicated research agent. Do not enable built-in terminal, arbitrary-code browser, filesystem, payment, messaging or other side-effect tools for this profile. Do not give the runner household storage or model/railway secrets unnecessarily.
5. Verify one synthetic actual model → plugin → private worker → observation round trip before marking Hermes connected. Use a fresh Hermes session with memory/context files disabled for this research profile; never load personal contexts into public-page research.

The plugin returns evidence, not a payment, order, reservation, or authoritative live-status guarantee. It does not manage the hosted website's visitor task state. This bridge prepares a safe integration boundary; it does not by itself replace the website's orchestrator or configure WhatsApp.
