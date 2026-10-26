import tempfile
import unittest
from pathlib import Path

from home_agent.errors import AppError
from home_agent.service import HomeAgent


class CheckoutHandoffTests(unittest.TestCase):
    def test_draft_never_approves_or_produces_receipt_and_is_owner_only(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = HomeAgent(Path(folder) / "test.db")
            args = {
                "kind": "food",
                "merchant_url": "https://example.com",
                "details": "Two dosas, less spicy",
            }
            task = agent.tool("checkout_handoff", args)
            self.assertEqual(task["status"], "needs_input")
            self.assertFalse(task["result"]["external_action_executed"])
            self.assertNotIn("receipt", task["result"])
            with self.assertRaises(AppError):
                agent.approve(task["id"])
            with self.assertRaises(AppError):
                agent.tool("checkout_handoff", args, "cook")
            with self.assertRaises(AppError):
                agent.tool(
                    "checkout_handoff",
                    {**args, "merchant_url": "https://example.com/checkout"},
                )
            self.assertEqual(agent.cancel(task["id"])["status"], "cancelled")
