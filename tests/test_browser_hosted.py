import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from home_agent.browser_client import BrowserClient
from home_agent.cloud_state import VisitorState
from home_agent.hosted import create_app
from test_browser_research import observation

BASE = "https://example.test"
HEADERS = {"Origin": BASE, "X-Home-Agent": "local-console"}


class BrowserHostedTests(unittest.TestCase):
    def test_ownership_restart_retry_and_model_independent_inspection(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = VisitorState(root=Path(folder), bucket="")
            calls = []

            def inspect(payload):
                calls.append(payload)
                return observation(payload)

            app = create_app(repo, browser=BrowserClient(transport=inspect))
            client, other = app.test_client(), app.test_client()
            for visitor in [client, other]:
                visitor.get("/api/state", base_url=BASE)

            def post(visitor, path, data):
                return visitor.post(path, json=data, headers=HEADERS, base_url=BASE)

            task = post(
                client,
                "/api/browser/tasks",
                {
                    "goal": "Inspect",
                    "url": "https://example.com",
                    "mode": "inspect",
                    "request_id": "one",
                },
            ).json
            path = f"/api/browser/tasks/{task['id']}/steps"
            self.assertEqual(post(other, path, {"version": 0}).status_code, 404)
            with patch("home_agent.research.post_json") as model:
                done = post(client, path, {"version": 0})
                duplicate = post(client, path, {"version": 0})
                model.assert_not_called()
            self.assertEqual(done.status_code, 200)
            self.assertEqual(done.json, duplicate.json)
            self.assertEqual(len(calls), 1)
            stored = client.get("/api/state", base_url=BASE).json["tasks"][0]
            self.assertEqual(stored["result"]["pages"][0]["title"], "Example")
            self.assertEqual(
                post(client, f"/api/tasks/{task['id']}/approval", {}).status_code, 409
            )
            self.assertEqual(
                post(
                    client,
                    "/api/browser/tasks",
                    {"goal": "Inspect", "url": "https://127.0.0.1"},
                ).status_code,
                422,
            )
