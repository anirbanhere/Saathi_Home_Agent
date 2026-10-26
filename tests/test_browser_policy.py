import unittest
from home_agent.errors import AppError
from home_agent.browser_policy import public_url, public_addresses, validate_actions


class BrowserPolicyTests(unittest.TestCase):
    def test_only_public_https_without_credentials_or_custom_ports(self):
        for url in [
            "http://example.com",
            "file:///etc/passwd",
            "https://localhost/",
            "https://127.0.0.1/",
            "https://[::1]/",
            "https://169.254.169.254/",
            "https://metadata.google.internal/",
            "https://user:pass@example.com",
            "https://example.com:8080",
            "https://example.com/?access_token=secret",
        ]:
            with self.subTest(url=url), self.assertRaises(AppError):
                public_url(url)
        self.assertEqual(
            public_url("https://example.com/news#top"), "https://example.com/news"
        )

    def test_dns_must_resolve_only_to_public_addresses(self):
        def mixed(*args, **kwargs):
            return [(2, 1, 6, "", ("8.8.8.8", 443)), (2, 1, 6, "", ("10.0.0.1", 443))]

        with self.assertRaises(AppError):
            public_addresses("example.com", resolver=mixed)

        def public(*args, **kwargs):
            return [(2, 1, 6, "", ("8.8.8.8", 443))]

        self.assertEqual(public_addresses("example.com", resolver=public), ["8.8.8.8"])

    def test_auth_and_transaction_destinations_require_handoff(self):
        for path in [
            "/login",
            "/checkout",
            "/payment",
            "/orders/submit",
            "/account/profile",
            "/cart/add",
        ]:
            with self.subTest(path=path), self.assertRaises(AppError):
                public_url("https://example.com" + path)

    def test_actions_are_declarative_bounded_and_never_execute_code(self):
        valid = [
            {"type": "fill", "selector": "#flight", "value": "AI101"},
            {"type": "click", "selector": "button.search"},
        ]
        self.assertEqual(validate_actions(valid), valid)
        for actions in [
            [{"type": "evaluate", "code": "alert(1)"}],
            [{"type": "upload", "selector": "input"}],
            valid * 5,
            [{"type": "fill", "selector": "input", "value": "sk-or-v1-secret"}],
            [{"type": "click", "selector": "button", "approved": True}],
        ]:
            with self.subTest(actions=actions), self.assertRaises(AppError):
                validate_actions(actions)
