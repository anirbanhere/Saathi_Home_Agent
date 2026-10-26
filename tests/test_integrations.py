import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from home_agent.errors import AppError
from home_agent.integrations import MusePlanner, parse_plan
from home_agent.mcp import dispatch
from home_agent.service import HomeAgent


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent.parent / "data" / "test-temp"
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.app = HomeAgent(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def test_muse_configuration_fails_closed_without_credentials(self):
        with self.assertRaises(AppError):
            MusePlanner(key="")

    def test_model_cannot_approve_a_payment_or_add_arguments(self):
        for call in [
            {"name": "approve", "arguments": '{"task_id":"any"}'},
            {"name": "train_status", "arguments": '{"train_number":"12627","date":"2026-11-01","approve":true}'},
        ]:
            with self.assertRaises(AppError):
                parse_plan({"choices": [{"message": {"tool_calls": [{"function": call}]}}]})

    def test_provider_response_is_validated(self):
        for response in [{}, {"choices": []}, {"choices": [{"message": {"content": 5}}]}]:
            with self.assertRaises(AppError):
                parse_plan(response)

    def test_function_call_and_muse_message_are_persisted(self):
        planner = MusePlanner(key="test-placeholder")
        response = {"choices": [{"message": {"tool_calls": [{"function": {
            "name": "train_status", "arguments": json.dumps({"train_number": "12627", "date": "2026-11-01"})}}]}}]}
        with patch("home_agent.integrations.post_json", return_value=response):
            result = planner.message(self.app, "Check my train", "ta", "model-test", "message-1")
            repeated = planner.message(self.app, "Check my train", "ta", "model-test", "message-1")
        self.assertEqual(result, repeated)
        self.assertEqual(result["mode"], "meta-model-api")
        self.assertEqual(result["task"]["result"]["mode"], "fixture")
        self.assertEqual(len(self.app.snapshot(session="model-test")["messages"]), 1)

    def test_mcp_discovery_excludes_approval_and_mutating_stock_tools(self):
        result = dispatch(self.app, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, "cook")
        names = {tool["name"] for tool in result["result"]["tools"]}
        self.assertEqual(names, {"inventory_list", "recipe_plan", "dish_suggestions", "task_status"})

    def test_mcp_cannot_impersonate_owner(self):
        response = dispatch(self.app, {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "bill_preview", "arguments": {"account": "DEMO-1042", "actor": "owner"}}}, "cook")
        self.assertTrue(response["result"]["isError"])

    def test_mcp_initialization_and_notification(self):
        request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}}
        response = dispatch(self.app, request, "owner")
        self.assertEqual(response["result"]["serverInfo"]["name"], "home-agent")
        self.assertIsNone(dispatch(self.app, {"jsonrpc": "2.0", "method": "notifications/initialized"}, "owner"))
