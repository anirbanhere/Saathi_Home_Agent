import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch

from home_agent.server import make_server
from home_agent.service import HomeAgent


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parent.parent / "data" / "test-temp"
        root.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=root)
        cls.server = make_server(HomeAgent(Path(cls.temp.name) / "test.sqlite3"), port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        merged = {"Content-Type": "application/json", "X-Home-Agent": "local-console"}
        merged.update(headers or {})
        conn.request(method, path, json.dumps(body) if body is not None else None, merged)
        response = conn.getresponse()
        payload = response.read()
        result = (response.status, dict(response.getheaders()), payload)
        conn.close()
        return result

    def test_static_and_state_have_security_headers(self):
        status, headers, data = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Home Agent", data)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        status, _, data = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        state = json.loads(data)
        self.assertIn("integrations", state)
        self.assertNotIn("key", state["integrations"])

    def test_cross_origin_and_dns_rebinding_are_rejected(self):
        status, _, _ = self.request("POST", "/api/messages", {"text": "hello"}, {"Origin": "https://evil.example"})
        self.assertEqual(status, 403)
        status, _, _ = self.request("GET", "/api/state", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)

    def test_oversized_body_and_invalid_json_fail_with_public_errors(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("POST", "/api/messages", b"{", {"Content-Type": "application/json", "X-Home-Agent": "local-console"})
        response = conn.getresponse()
        self.assertEqual(response.status, 422)
        self.assertIn("error", json.loads(response.read()))
        conn.close()
        status, _, _ = self.request("POST", "/api/messages", {"text": "hi"}, {"Content-Length": "9000000"})
        self.assertEqual(status, 413)

    def test_messages_and_task_approval_work_through_http(self):
        status, _, data = self.request("POST", "/api/tools", {"name": "bill_preview", "arguments": {"account": "DEMO-1042"}})
        self.assertEqual(status, 200)
        task = json.loads(data)
        status, _, data = self.request("POST", f"/api/tasks/{task['id']}/approval", {})
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(data)["result"]["receipt"].startswith("SANDBOX-"))

    def test_missing_speech_or_muse_key_does_not_pretend_to_work(self):
        with patch.dict("os.environ", {"MODEL_API_KEY": ""}):
            status, _, data = self.request("POST", "/api/messages", {"text": "hello", "engine": "muse"})
        self.assertEqual(status, 503)
        self.assertEqual(json.loads(data)["error"]["code"], "NOT_CONFIGURED")

    def test_unknown_routes_and_invalid_types_are_safe(self):
        for path, body in [("/api/messages", {"text": []}), ("/api/tools", {"name": [], "arguments": {}})]:
            status, _, data = self.request("POST", path, body)
            self.assertEqual(status, 422)
            self.assertNotIn(b"Traceback", data)
        self.assertEqual(self.request("GET", "/../README.md")[0], 404)
