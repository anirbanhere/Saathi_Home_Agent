"""Loopback-only UI QA fixtures. Never deploy; no provider requests are made.

Run: python tests/ui_fixture_server.py
Browse: http://127.0.0.1:8766 (use a fresh browser context).
"""

import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from home_agent.browser_client import BrowserClient
from home_agent.cloud_state import VisitorState
from home_agent.errors import AppError
from home_agent.hosted import create_app
from home_agent.model_catalog import ModelCatalog


def observation(payload):
    time.sleep(1)  # Make progress/focus checks reproducible without network timing.
    blocked = "/blocked" in payload["url"]
    return {
        "url": payload["url"],
        "title": "Synthetic blocked page" if blocked else "Synthetic public source",
        "text": "SYNTHETIC UI FIXTURE. <script>alert('untrusted')</script> Flight ZX123 has no verified live status.",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "profile": "public_readonly",
        "state": "needs_input" if blocked else "observed",
        "http_status": 403 if blocked else 200,
        "controls": [],
        "links": [],
    }


if __name__ == "__main__":
    # Explicit replacements prevent inherited developer credentials/config from use.
    with tempfile.TemporaryDirectory(prefix="home-agent-ui-") as folder, patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "synthetic-ui-fixture",
            "RAILRADAR_API_KEY": "",
            "MODEL_API_KEY": "",
            "HOME_AGENT_ASR_URL": "",
            "HOME_AGENT_TTS_URL": "",
            "HOME_AGENT_TRAIN_PROVIDER": "fixture",
            "HOME_AGENT_PUBLIC_ORIGIN": "",
        },
    ), patch(
        "home_agent.research.post_json",
        side_effect=AppError("Synthetic model capacity failure. Saved sources are retained.", 429, "RATE_LIMITED"),
    ), patch(
        "home_agent.agent_loop.post_json",
        side_effect=AppError("Synthetic model capacity failure.", 429, "RATE_LIMITED"),
    ):
        catalog = ModelCatalog(loader=lambda key: {"data": [{
            "id": "fixture/ui:free", "supported_parameters": ["tools", "tool_choice"],
            "pricing": {"prompt": "0", "completion": "0"},
        }]})
        app = create_app(
            VisitorState(root=Path(folder), bucket=""),
            model_catalog=catalog,
            browser=BrowserClient(transport=observation),
        )
        app.run(host="127.0.0.1", port=8766, debug=False, use_reloader=False, load_dotenv=False)
