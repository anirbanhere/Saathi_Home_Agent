import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from home_agent.browser_client import BrowserClient
from test_browser_research import observation


class HermesBridgeTests(unittest.TestCase):
    def test_registers_only_restricted_tool_and_runs_validated_handler(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "integrations/hermes-public-browser/__init__.py"
        )
        spec = importlib.util.spec_from_file_location("saathi_plugin", path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)

        class Registry:
            def register_tool(self, **kwargs):
                self.tool = kwargs

        registry = Registry()
        plugin.register(registry)
        self.assertEqual(registry.tool["toolset"], "saathi_public_browser")
        self.assertEqual(
            set(registry.tool["schema"]["parameters"]["properties"]), {"url", "actions"}
        )
        client = BrowserClient(transport=observation)
        with patch.object(plugin, "BrowserClient", return_value=client):
            result = json.loads(
                registry.tool["handler"]({"url": "https://example.com"})
            )
            self.assertTrue(result["success"])
            result = json.loads(plugin.handle({"url": "https://127.0.0.1"}))
            self.assertFalse(result["success"])
            result = json.loads(
                plugin.handle({"url": "https://example.com", "code": "print('unsafe')"})
            )
            self.assertFalse(result["success"])
