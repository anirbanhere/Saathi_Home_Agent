import unittest
from home_agent.errors import AppError
from home_agent.model_catalog import ModelCatalog


def model(identifier, tools=True, price="0"):
    return {"id": identifier, "supported_parameters": ["tools", "tool_choice"] if tools else [],
            "pricing": {"prompt": price, "completion": price}}


class CatalogTests(unittest.TestCase):
    def test_only_key_permitted_free_tool_models_are_offered(self):
        catalog = ModelCatalog(loader=lambda key: {"data": [
            model("google/gemma-4-26b-a4b-it:free"), model("vendor/paid"),
            model("vendor/no-tools:free", tools=False), model("vendor/paid-tag:free", price="0.001")
        ]})
        result = catalog.status("key")
        self.assertTrue(result["verified"])
        self.assertEqual(result["models"], ["google/gemma-4-26b-a4b-it:free"])

    def test_cache_refreshes_after_expiry_and_key_change(self):
        clock, calls = [0], []
        def load(key):
            calls.append(key)
            return {"data": [model("google/gemma-4-26b-a4b-it:free")]}
        catalog = ModelCatalog(loader=load, clock=lambda: clock[0])
        catalog.status("one"); catalog.status("one")
        self.assertEqual(len(calls), 1)
        clock[0] = 61
        catalog.status("one")
        catalog.status("two")
        self.assertEqual(len(calls), 3)

    def test_error_does_not_turn_known_blocked_models_into_choices(self):
        def unavailable(key):
            raise AppError("upstream")
        result = ModelCatalog(loader=unavailable).status("key")
        self.assertFalse(result["verified"])
        self.assertEqual(result["models"], [])
        self.assertEqual(result["code"], "MODEL_CATALOG_UNAVAILABLE")

    def test_empty_catalog_and_missing_key_are_distinct(self):
        catalog = ModelCatalog(loader=lambda key: {"data": []})
        self.assertEqual(catalog.status("")["code"], "NOT_CONFIGURED")
        result = catalog.status("key")
        self.assertTrue(result["verified"])
        self.assertEqual(result["code"], "NO_PERMITTED_MODELS")

    def test_malformed_provider_catalog_fails_closed(self):
        result = ModelCatalog(loader=lambda key: {"data": "not-models"}).status("key")
        self.assertFalse(result["verified"])
        self.assertEqual(result["models"], [])
