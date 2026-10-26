import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from home_agent.browser_client import BrowserClient
from home_agent.errors import AppError
from home_agent.service import HomeAgent
from home_agent.research import ResearchTasks


def observation(payload):
    return {
        "url": payload["url"],
        "title": "Example",
        "text": "Flight ZX123 is scheduled. No live movement report is available.",
        "observed_at": "2026-10-26T12:00:00+00:00",
        "profile": "public_readonly",
        "state": "observed",
        "controls": [],
        "links": [],
    }


class ResearchTests(unittest.TestCase):
    def test_blocked_page_cannot_support_a_completed_answer(self):
        import json

        engine = ResearchTasks(
            BrowserClient(
                transport=lambda payload: {
                    **observation(payload),
                    "state": "needs_input",
                    "http_status": 403,
                }
            )
        )
        task = engine.start(
            self.app, "Find status", "https://example.com", "agent", "vendor/model:free"
        )
        engine.advance(self.app, task["id"], 0)
        output = {
            "choices": [
                {
                    "message": {
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "finish_research",
                                    "arguments": json.dumps(
                                        {
                                            "summary": "Flight arrived",
                                            "page_index": 0,
                                            "evidence_quote": "Flight ZX123 is scheduled.",
                                        }
                                    ),
                                }
                            }
                        ]
                    }
                }
            ]
        }
        with patch("home_agent.research.post_json", return_value=output):
            result = engine.advance(self.app, task["id"], 1, key="synthetic")
        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(
            result["result"]["last_error"]["code"], "RESEARCH_EVIDENCE_MISSING"
        )

    def test_six_step_budget_stops_repeated_provider_retries(self):
        task = self.engine.start(self.app, "Inspect", "", "agent", "vendor/model:free")
        with patch(
            "home_agent.research.post_json",
            side_effect=AppError("Busy", 429, "RATE_LIMITED"),
        ) as model:
            for version in range(7):
                task = self.engine.advance(
                    self.app, task["id"], version, key="synthetic"
                )
        self.assertEqual(task["status"], "failed")
        self.assertEqual(model.call_count, 6)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = HomeAgent(Path(self.temp.name) / "test.sqlite3")
        self.engine = ResearchTasks(BrowserClient(transport=observation))

    def tearDown(self):
        self.temp.cleanup()

    def test_direct_inspection_is_persistent_and_idempotent_without_model(self):
        task = self.engine.start(
            self.app,
            "Inspect page",
            "https://example.com",
            "inspect",
            "",
            request_id="one",
        )
        again = self.engine.start(
            self.app,
            "Inspect page",
            "https://example.com",
            "inspect",
            "",
            request_id="one",
        )
        self.assertEqual(task["id"], again["id"])
        with patch("home_agent.research.post_json") as model:
            done = self.engine.advance(self.app, task["id"], 0)
            duplicate = self.engine.advance(self.app, task["id"], 0)
            model.assert_not_called()
        self.assertEqual(done, duplicate)
        self.assertEqual(done["status"], "succeeded")
        self.assertEqual(done["result"]["pages"][0]["url"], "https://example.com/")

    def test_model_outage_keeps_page_evidence_for_resume(self):
        task = self.engine.start(
            self.app, "Find status", "https://example.com", "agent", "vendor/model:free"
        )
        observed = self.engine.advance(self.app, task["id"], 0)
        self.assertEqual(observed["status"], "running")
        with patch(
            "home_agent.research.post_json",
            side_effect=AppError("Provider busy", 429, "RATE_LIMITED"),
        ):
            blocked = self.engine.advance(self.app, task["id"], 1, key="synthetic")
        self.assertEqual(blocked["status"], "needs_input")
        self.assertEqual(len(blocked["result"]["pages"]), 1)

    def test_final_answer_requires_quote_from_inspected_page(self):
        task = self.engine.start(
            self.app, "Find status", "https://example.com", "agent", "vendor/model:free"
        )
        self.engine.advance(self.app, task["id"], 0)

        def response(quote):
            import json

            return {
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "finish_research",
                                        "arguments": json.dumps(
                                            {
                                                "summary": "Only a schedule was found.",
                                                "page_index": 0,
                                                "evidence_quote": quote,
                                            }
                                        ),
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

        with patch(
            "home_agent.research.post_json",
            return_value=response("invented live position"),
        ):
            invalid = self.engine.advance(self.app, task["id"], 1, key="synthetic")
        self.assertEqual(invalid["status"], "needs_input")
        with patch(
            "home_agent.research.post_json",
            return_value=response("No live movement report is available."),
        ):
            done = self.engine.advance(self.app, task["id"], 2, key="synthetic")
        self.assertEqual(done["status"], "succeeded")
        self.assertEqual(
            done["result"]["citation"]["quote"], "No live movement report is available."
        )

    def test_no_observations_cannot_become_a_verified_answer(self):
        task = self.engine.start(
            self.app, "Find flight status", "", "agent", "vendor/model:free"
        )
        import json

        output = {
            "choices": [
                {
                    "message": {
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "finish_research",
                                    "arguments": json.dumps(
                                        {
                                            "summary": "Arrived",
                                            "page_index": 0,
                                            "evidence_quote": "Arrived",
                                        }
                                    ),
                                }
                            }
                        ]
                    }
                }
            ]
        }
        with patch("home_agent.research.post_json", return_value=output):
            result = self.engine.advance(self.app, task["id"], 0, key="synthetic")
        self.assertEqual(result["status"], "needs_input")

    def test_other_visitor_cannot_access_job_and_cancel_stops_execution(self):
        task = self.engine.start(
            self.app, "Inspect", "https://example.com", "inspect", ""
        )
        other = HomeAgent(Path(self.temp.name) / "other.sqlite3")
        with self.assertRaises(AppError):
            self.engine.advance(other, task["id"], 0)
        self.app.cancel(task["id"])
        result = self.engine.advance(self.app, task["id"], 0)
        self.assertEqual(result["status"], "cancelled")

    def test_worker_response_validation_and_credential_free_payload(self):
        sent = []

        def transport(payload):
            sent.append(payload)
            return observation(payload)

        BrowserClient(transport=transport).observe("https://example.com", [])
        self.assertEqual(set(sent[0]), {"url", "actions"})
        with self.assertRaises(AppError):
            BrowserClient(transport=lambda payload: {"profile": "admin"}).observe(
                "https://example.com"
            )
