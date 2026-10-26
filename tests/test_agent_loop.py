import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from home_agent.errors import AppError
from home_agent.service import HomeAgent
from home_agent.agent_loop import FreeModelAgent
from home_agent.integrations import post_json


def call(name, arguments, identifier="call-1"):
    return {"choices": [{"message": {"content": None, "tool_calls": [
        {"id": identifier, "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}
    ]}}]}


def reply(content):
    return {"choices": [{"message": {"content": content}}]}


class AgentLoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = HomeAgent(Path(self.temp.name) / "agent.sqlite3")
        self.agent = FreeModelAgent(key="test-key", model="openrouter/free")

    def tearDown(self):
        self.temp.cleanup()

    def test_tools_are_observed_and_reply_is_saved_once(self):
        with patch("home_agent.agent_loop.post_json", side_effect=[
            call("inventory_list", {}), call("recipe_plan", {"recipe": "dal"}, "call-2"),
            reply("Here is the plan. Review the quantities before cooking.")
        ]) as provider:
            result = self.agent.message(self.app, "Use my inventory to plan dal", "en", "chat", "request-1")
            cached = self.agent.message(self.app, "Use my inventory to plan dal", "en", "chat", "request-1")
        self.assertEqual(result, cached)
        self.assertEqual(provider.call_count, 3)
        observations = provider.call_args_list[1].args[1]["messages"]
        self.assertTrue(any(x["role"] == "tool" and "inventory_list" in x["content"] for x in observations))
        self.assertEqual(len(result["trace"]), 2)
        self.assertEqual(result["task"]["status"], "planned")
        self.assertEqual(len(self.app.snapshot(session="chat")["messages"]), 1)

    def test_model_cannot_approve_or_mutate_stock(self):
        with patch("home_agent.agent_loop.post_json", return_value=call("approve", {"task_id": "x"})):
            with self.assertRaises(AppError):
                self.agent.message(self.app, "Pay it", "en", "chat", "request-2")
        self.assertEqual(self.app.snapshot()["metrics"]["sandbox_payments"], 0)

    def test_paid_models_are_rejected_before_network(self):
        with self.assertRaises(AppError):
            FreeModelAgent(key="test", model="provider/paid-model")

    def test_request_id_conflict_and_missing_key(self):
        with patch("home_agent.agent_loop.post_json", return_value=reply("Which dish?")):
            self.agent.message(self.app, "Cook", "en", "chat", "same-id")
            with self.assertRaises(AppError):
                self.agent.message(self.app, "Pay", "en", "chat", "same-id")
        with self.assertRaises(AppError):
            FreeModelAgent(key="")

    def test_loop_limit_returns_observed_task_without_inventing_result(self):
        with patch("home_agent.agent_loop.post_json", return_value=call("inventory_list", {})) as provider:
            result = self.agent.message(self.app, "What is there?", "en", "chat", "bounded")
        self.assertEqual(provider.call_count, 3)
        self.assertEqual(result["task"]["kind"], "inventory_list")
        self.assertEqual(result["reply"], result["task"]["result"]["summary"])

    def test_sandbox_receipt_never_created_by_model(self):
        with patch("home_agent.agent_loop.post_json", side_effect=[call("bill_preview", {"account": "DEMO-1042"}), reply("Please review and approve the bill card.")]):
            result = self.agent.message(self.app, "Pay my demo bill", "hi", "chat", "bill")
        self.assertEqual(result["task"]["status"], "awaiting_approval")
        self.assertNotIn("receipt", result["task"]["result"])

    def test_provider_capacity_error_is_a_recoverable_429(self):
        with patch("home_agent.integrations.build_opener") as opener:
            opener.return_value.open.side_effect = HTTPError("https://openrouter.ai", 429, "busy", {}, None)
            with self.assertRaises(AppError) as error:
                post_json("https://openrouter.ai/api/v1/chat/completions", {}, "test")
        self.assertEqual(error.exception.status, 429)
        self.assertEqual(error.exception.code, "RATE_LIMITED")
