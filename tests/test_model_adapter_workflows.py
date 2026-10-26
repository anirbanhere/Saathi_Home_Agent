import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from home_agent.agent_loop import FreeModelAgent
from home_agent.errors import AppError
from home_agent.integrations import MusePlanner
from home_agent.model_adapters import MetaAdapter, OpenRouterAdapter
from home_agent.service import HomeAgent


def tool_response():
    return {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "id": "read-stock",
                            "type": "function",
                            "function": {"name": "inventory_list", "arguments": "{}"},
                        }
                    ]
                }
            }
        ]
    }


class AdapterWorkflowTests(unittest.TestCase):
    def test_same_inventory_workflow_and_replay_across_adapter_implementations(self):
        with tempfile.TemporaryDirectory() as folder:
            for provider in ["openrouter", "meta"]:
                with self.subTest(provider=provider):
                    app = HomeAgent(Path(folder) / (provider + ".db"))
                    if provider == "openrouter":
                        transport = Mock(
                            side_effect=[
                                tool_response(),
                                {
                                    "choices": [
                                        {
                                            "message": {
                                                "content": "The stock list is saved."
                                            }
                                        }
                                    ]
                                },
                            ]
                        )
                        adapter = OpenRouterAdapter(
                            "synthetic", "test/model:free", transport=transport
                        )
                        planner = FreeModelAgent(
                            key="synthetic", model="test/model:free", adapter=adapter
                        )
                    else:
                        transport = Mock(return_value=tool_response())
                        adapter = MetaAdapter(
                            "synthetic", "test-meta", transport=transport
                        )
                        planner = MusePlanner(
                            key="synthetic", model="test-meta", adapter=adapter
                        )
                    first = planner.message(
                        app, "List my stock", "ta", "same-task", "same-request"
                    )
                    count = transport.call_count
                    again = planner.message(
                        app, "List my stock", "ta", "same-task", "same-request"
                    )
                    self.assertEqual(first, again)
                    self.assertEqual(transport.call_count, count)
                    self.assertEqual(first["task"]["kind"], "inventory_list")
                    self.assertEqual(
                        first["task"]["result"]["items"],
                        app.tool("inventory_list", {})["result"]["items"],
                    )
                    self.assertEqual(
                        len(app.snapshot(session="same-task")["messages"]), 1
                    )

    def test_free_agent_rejects_cross_provider_adapter(self):
        with self.assertRaises(AppError):
            FreeModelAgent(
                key="synthetic",
                model="test/model:free",
                adapter=MetaAdapter("synthetic", "test/model:free"),
            )

    def test_embedded_followup_outage_keeps_verified_result_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            app = HomeAgent(Path(folder) / "test.db")
            send = Mock(
                side_effect=[
                    tool_response(),
                    {"error": {"code": 429, "message": "raw upstream detail"}},
                ]
            )
            adapter = OpenRouterAdapter("synthetic", "test/model:free", transport=send)
            planner = FreeModelAgent(
                key="synthetic", model="test/model:free", adapter=adapter
            )
            result = planner.message(app, "Read stock", "en", "chat", "outage")
            again = planner.message(app, "Read stock", "en", "chat", "outage")
            self.assertEqual(result, again)
            self.assertEqual(result["task"]["status"], "succeeded")
            self.assertEqual(result["verified_actions"], 1)
            self.assertIn("follow-up unavailable", result["notice"])
            self.assertNotIn("raw upstream", json.dumps(result))
            self.assertEqual(send.call_count, 2)
