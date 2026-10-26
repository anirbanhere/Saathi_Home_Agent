import unittest
from unittest.mock import Mock

from home_agent.errors import AppError
from home_agent.model_adapters import CompletionRequest, MetaAdapter, OpenRouterAdapter


def response(message=None, **extra):
    return {
        "choices": [{"message": message or {"content": "Observed stock."}}],
        **extra,
    }


class AdapterTests(unittest.TestCase):
    def request(self):
        return CompletionRequest(
            messages=[{"role": "user", "content": "Read stock"}], tools=[]
        )

    def test_provider_payloads_and_results_share_one_contract(self):
        for adapter_type, model, token_field, provider in [
            (OpenRouterAdapter, "test/model:free", "max_tokens", "openrouter"),
            (MetaAdapter, "test-meta", "max_completion_tokens", "meta"),
        ]:
            with self.subTest(provider=provider):
                send = Mock(
                    return_value=response(
                        model=model,
                        usage={
                            "prompt_tokens": 12,
                            "completion_tokens": 4,
                            "secret": "do not retain",
                        },
                    )
                )
                adapter = adapter_type("synthetic-key", model, transport=send)
                result = adapter.complete(self.request())
                url, payload, key = send.call_args.args
                self.assertEqual(key, "synthetic-key")
                self.assertEqual(payload[token_field], 1400)
                self.assertEqual(payload["model"], model)
                self.assertEqual(result.message["content"], "Observed stock.")
                self.assertEqual(result.model, model)
                self.assertEqual(
                    result.usage, {"prompt_tokens": 12, "completion_tokens": 4}
                )
                self.assertGreaterEqual(result.elapsed_ms, 0)
                self.assertEqual(adapter.profile.provider, provider)
                self.assertNotIn("synthetic-key", repr(adapter))
                if provider == "openrouter":
                    self.assertEqual(
                        url, "https://openrouter.ai/api/v1/chat/completions"
                    )
                    self.assertEqual(payload["provider"], {"require_parameters": True})
                else:
                    self.assertNotIn("provider", payload)

    def test_free_policy_and_credential_endpoint_separation(self):
        for build in [
            lambda: OpenRouterAdapter("synthetic", "paid/model"),
            lambda: OpenRouterAdapter("sk-nous-synthetic", "test/model:free"),
            lambda: MetaAdapter("sk-or-synthetic", "test-meta"),
            lambda: MetaAdapter(
                "synthetic",
                "test-meta",
                base_url="https://user:password@example.com/v1",
            ),
            lambda: MetaAdapter(
                "synthetic", "test-meta", base_url="http://example.com/v1"
            ),
            lambda: MetaAdapter(
                "synthetic", "test-meta", base_url="https://openrouter.ai/api/v1"
            ),
            lambda: MetaAdapter(
                "synthetic", "test-meta", base_url="https://[invalid/v1"
            ),
        ]:
            with self.subTest(build=build), self.assertRaises(AppError):
                build()

    def test_invalid_responses_fail_with_normalized_error(self):
        for payload in [
            {},
            {"choices": []},
            {"choices": [{"message": []}]},
            response({"content": 7}),
            response({"content": "x" * 8001}),
            response({"tool_calls": "invalid"}),
        ]:
            with self.subTest(payload_type=type(payload).__name__):
                adapter = OpenRouterAdapter(
                    "synthetic", "test/model:free", transport=lambda *args: payload
                )
                with self.assertRaises(AppError) as caught:
                    adapter.complete(self.request())
                self.assertEqual(caught.exception.code, "INVALID_MODEL_OUTPUT")

    def test_embedded_rate_limit_is_not_misclassified_as_invalid_output(self):
        adapter = OpenRouterAdapter(
            "synthetic",
            "test/model:free",
            transport=lambda *args: {
                "error": {"code": 429, "message": "sensitive raw provider details"}
            },
        )
        with self.assertRaises(AppError) as caught:
            adapter.complete(self.request())
        self.assertEqual(caught.exception.code, "RATE_LIMITED")
        self.assertNotIn("sensitive", str(caught.exception))

    def test_request_snapshot_and_tool_calls_survive_normalization(self):
        call = {
            "id": "call-one",
            "type": "function",
            "function": {"name": "inventory_list", "arguments": "{}"},
        }
        send = Mock(return_value=response({"content": None, "tool_calls": [call]}))
        request = self.request()
        result = OpenRouterAdapter(
            "synthetic", "test/model:free", transport=send
        ).complete(request)
        request.messages.append({"role": "tool", "content": "later observation"})
        self.assertEqual(len(send.call_args.args[1]["messages"]), 1)
        self.assertEqual(result.message["tool_calls"], [call])

    def test_observer_gets_only_profile_outcome_and_duration(self):
        observer = Mock()
        adapter = OpenRouterAdapter(
            "synthetic-secret",
            "test/model:free",
            transport=lambda *args: response(),
            on_result=observer,
        )
        adapter.complete(self.request())
        profile = observer.call_args.args[0]
        self.assertEqual(profile.model, "test/model:free")
        self.assertNotIn("synthetic-secret", repr(profile))
        self.assertIn("elapsed_ms", observer.call_args.kwargs)
        failure = AppError("Provider busy", 429, "RATE_LIMITED")
        adapter.transport = Mock(side_effect=failure)
        with self.assertRaises(AppError):
            adapter.complete(self.request())
        self.assertEqual(observer.call_args.kwargs["error"].code, "RATE_LIMITED")

    def test_invalid_request_budget_fails_before_transport(self):
        for budget in [True, 0, 50000]:
            with self.assertRaises(AppError):
                CompletionRequest(
                    messages=[{"role": "user", "content": "Hi"}],
                    tools=[],
                    max_tokens=budget,
                )

    def test_untrusted_usage_numbers_cannot_break_a_valid_completion(self):
        for value in [10**1000, float("inf"), float("nan"), -1, True]:
            with self.subTest(value_type=type(value).__name__):
                adapter = OpenRouterAdapter(
                    "synthetic",
                    "test/model:free",
                    transport=lambda *args: response(usage={"prompt_tokens": value}),
                )
                result = adapter.complete(self.request())
                self.assertEqual(result.usage, {})

    def test_transport_errors_are_sanitized_and_distinguished(self):
        from urllib.error import HTTPError
        from unittest.mock import patch
        from home_agent.integrations import post_json

        for status, code in [
            (401, "MODEL_AUTH_ERROR"),
            (403, "MODEL_NOT_ALLOWED"),
            (402, "PROVIDER_QUOTA_EXCEEDED"),
            (408, "PROVIDER_TIMEOUT"),
            (503, "PROVIDER_UNAVAILABLE"),
        ]:
            with self.subTest(status=status), patch(
                "home_agent.integrations.build_opener"
            ) as opener:
                opener.return_value.open.side_effect = HTTPError(
                    "https://openrouter.ai", status, "secret raw message", {}, None
                )
                with self.assertRaises(AppError) as caught:
                    post_json(
                        "https://openrouter.ai/api/v1/chat/completions", {}, "synthetic"
                    )
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn("secret raw", str(caught.exception))
