import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from home_agent.browser_client import BrowserClient
from home_agent.cloud_state import VisitorState
from home_agent.hosted import create_app
from home_agent.model_catalog import ModelCatalog
from test_browser_research import observation

MODEL = "test/model:free"
BASE = "https://example.test"
HEADERS = {"Origin": BASE, "X-Home-Agent": "local-console"}


class HostedHealthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        catalog = ModelCatalog(
            loader=lambda key: {
                "data": [
                    {
                        "id": MODEL,
                        "pricing": {"prompt": "0", "completion": "0"},
                        "supported_parameters": ["tools", "tool_choice"],
                    }
                ]
            }
        )
        self.app = create_app(
            VisitorState(root=Path(self.temp.name), bucket=""),
            model_catalog=catalog,
            browser=BrowserClient(transport=observation),
        )
        self.client = self.app.test_client()
        self.env = patch.dict(
            "os.environ", {"OPENROUTER_API_KEY": "synthetic", "OPENROUTER_MODEL": MODEL}
        )
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def state(self):
        return self.client.get("/api/state", base_url=BASE).json

    def post(self, path, body):
        return self.client.post(path, json=body, base_url=BASE, headers=HEADERS)

    def test_state_reports_observed_capacity_then_recovery_without_probing(self):
        self.assertEqual(
            self.state()["integrations"]["model_health"][MODEL]["state"], "unobserved"
        )
        with patch(
            "home_agent.agent_loop.post_json",
            return_value={"error": {"code": 429, "message": "private upstream detail"}},
        ) as provider:
            result = self.post(
                "/api/messages", {"text": "Synthetic read", "model": MODEL}
            )
            self.assertEqual(result.status_code, 429)
            state = self.state()
            self.state()
            self.assertEqual(provider.call_count, 1)
        health = state["integrations"]["model_health"]
        self.assertEqual(set(health), {MODEL})
        self.assertEqual(health[MODEL]["state"], "rate_limited")
        self.assertNotIn("private upstream", json.dumps(health))
        self.assertNotIn("Synthetic read", json.dumps(health))
        with patch(
            "home_agent.agent_loop.post_json",
            return_value={
                "choices": [{"message": {"content": "What would you like to inspect?"}}]
            },
        ):
            self.assertEqual(
                self.post(
                    "/api/messages", {"text": "Hello", "model": MODEL}
                ).status_code,
                200,
            )
        self.assertEqual(
            self.state()["integrations"]["model_health"][MODEL]["state"], "responding"
        )

    def test_research_rate_limit_records_health_and_retains_source(self):
        self.state()
        task = self.post(
            "/api/browser/tasks",
            {
                "goal": "Inspect",
                "url": "https://example.com",
                "mode": "agent",
                "model": MODEL,
            },
        ).json
        route = "/api/browser/tasks/" + task["id"] + "/steps"
        self.assertEqual(self.post(route, {"version": 0}).json["status"], "running")
        with patch(
            "home_agent.research.post_json", return_value={"error": {"code": 429}}
        ):
            paused = self.post(route, {"version": 1}).json
        self.assertEqual(paused["status"], "needs_input")
        self.assertEqual(len(paused["result"]["pages"]), 1)
        self.assertEqual(
            self.state()["integrations"]["model_health"][MODEL]["state"], "rate_limited"
        )
