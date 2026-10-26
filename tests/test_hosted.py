import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from home_agent.cloud_state import VisitorState
from home_agent.hosted import create_app

BASE = "https://example.test"
HEADERS = {"Origin": BASE, "X-Home-Agent": "local-console"}


class HostedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repository = VisitorState(root=Path(self.temp.name), bucket="")
        self.app = create_app(self.repository)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def get(self, client=None):
        return (client or self.client).get("/api/state", base_url=BASE)

    def post(self, path, data, client=None, headers=None):
        return (client or self.client).post(path, json=data, headers=HEADERS if headers is None else headers, base_url=BASE)

    def test_cookie_is_secure_and_visitors_have_separate_persistent_stock(self):
        initial = self.get()
        cookie = initial.headers["Set-Cookie"]
        for flag in ["Secure", "HttpOnly", "SameSite=Lax", "Path=/"]:
            self.assertIn(flag, cookie)
        response = self.post("/api/inventory/corrections", {"name": "rice", "quantity": 777, "unit": "g", "reference": "correction"})
        self.assertEqual(response.status_code, 200)
        other = self.app.test_client()
        def rice(response):
            return next(x["quantity"] for x in response.json["inventory"] if x["name"] == "rice")
        self.assertEqual(rice(self.get()), 777)
        self.assertNotEqual(rice(self.get(other)), 777)
        # New repository instance, same visitor credential, same persisted result.
        again = create_app(VisitorState(root=Path(self.temp.name), bucket="")).test_client()
        again.set_cookie("__Host-home-agent", self.client.get_cookie("__Host-home-agent", domain="example.test").value, domain="example.test")
        self.assertEqual(rice(self.get(again)), 777)

    def test_approval_is_visitor_scoped_and_repeat_safe(self):
        self.get()
        preview = self.post("/api/tools", {"name": "bill_preview", "arguments": {"account": "DEMO-1042"}}).json
        other = self.app.test_client()
        self.get(other)
        route = f"/api/tasks/{preview['id']}/approval"
        self.assertEqual(self.post(route, {}, other).status_code, 404)
        first, second = self.post(route, {}), self.post(route, {})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json["result"]["receipt"], second.json["result"]["receipt"])

    def test_origin_header_size_and_private_responses(self):
        self.get()
        self.assertEqual(self.post("/api/messages", {}, headers={"Origin": "https://evil.test", "X-Home-Agent": "local-console"}).status_code, 403)
        self.assertEqual(self.post("/api/messages", {}, headers={"Origin": BASE}).status_code, 403)
        self.assertEqual(self.client.post("/api/messages", data="x"*40000, content_type="application/json", headers=HEADERS, base_url=BASE).status_code, 413)
        state = self.get()
        self.assertEqual(state.headers["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", state.headers["Content-Security-Policy"])

    def test_unknown_task_is_not_leaked_and_user_cannot_supply_visitor(self):
        self.get()
        response = self.post("/api/tasks/" + "a"*32 + "/approval", {})
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("Traceback", response.text)
        state = self.client.get("/api/state?visitor=another&session=demo", base_url=BASE)
        self.assertEqual(state.status_code, 200)
        self.assertEqual(state.json["tasks"], [])

    def test_no_key_is_explicit_and_paid_model_is_rejected(self):
        self.get()
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}):
            response = self.post("/api/messages", {"engine": "openrouter", "text": "hi", "language": "en"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["error"]["code"], "NOT_CONFIGURED")
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test"}):
            response = self.post("/api/messages", {"engine": "openrouter", "model": "paid/model", "text": "hi", "language": "en"})
        self.assertEqual(response.status_code, 422)

    def test_mutation_without_visitor_cookie_requires_initialization(self):
        response = self.post("/api/tools", {"name": "inventory_list", "arguments": {}})
        self.assertEqual(response.status_code, 403)
