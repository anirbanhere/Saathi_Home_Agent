import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from home_agent.errors import AppError
from home_agent.service import HomeAgent


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        test_root = Path(__file__).resolve().parent.parent / "data" / "test-temp"
        test_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_root)
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.app = HomeAgent(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_billing_requires_human_approval_and_is_idempotent(self):
        task = self.app.tool("bill_preview", {"account": "DEMO-1042"})
        self.assertEqual(task["status"], "awaiting_approval")
        self.assertNotIn("receipt", task["result"])
        with self.assertRaises(AppError):
            self.app.tool("approve", {"task_id": task["id"]})
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.app.approve(task["id"]), range(4)))
        self.assertEqual(len({r["result"]["receipt"] for r in results}), 1)
        self.assertEqual(self.app.snapshot()["metrics"]["sandbox_payments"], 1)
        self.assertEqual(HomeAgent(self.path).task(task["id"])["status"], "succeeded")

    def test_cook_cannot_read_or_approve_bills(self):
        task = self.app.tool("bill_preview", {"account": "DEMO-1042"})
        for call in (
            lambda: self.app.tool("bill_preview", {"account": "DEMO-1042"}, actor="cook"),
            lambda: self.app.task(task["id"], actor="cook"),
            lambda: self.app.approve(task["id"], actor="cook"),
        ):
            with self.assertRaises(AppError) as error:
                call()
            self.assertEqual(error.exception.status, 403)

    def test_receipt_import_is_atomic_and_duplicate_safe(self):
        text = "Rice,1,kg\nTomato,250,g"
        first = self.app.import_receipt(text, "bill-001")
        second = self.app.import_receipt(text, "bill-001")
        self.assertEqual(first, second)
        rice = next(i for i in self.app.snapshot()["inventory"] if i["name"] == "rice")
        self.assertEqual(rice["quantity"], 2000)
        before = self.app.snapshot()["inventory"]
        with self.assertRaises(AppError):
            self.app.import_receipt("Rice,1,kg\nTomato,-5,g", "bad-bill")
        self.assertEqual(before, self.app.snapshot()["inventory"])
        with self.assertRaises(AppError):
            self.app.import_receipt("Rice,5,kg", "bill-001")

    def test_meal_is_estimated_and_deducted_once_after_completion(self):
        plan = self.app.tool("recipe_plan", {"recipe": "tomato-rice", "servings": 2})
        before = self.app.snapshot()["inventory"]
        self.assertEqual(before, self.app.snapshot()["inventory"])
        results = [self.app.complete_meal(plan["id"]), self.app.complete_meal(plan["id"])]
        self.assertEqual(results[0]["result"]["meal_id"], results[1]["result"]["meal_id"])
        rice = next(i for i in self.app.snapshot()["inventory"] if i["name"] == "rice")
        self.assertEqual(rice["quantity"], 800)
        self.assertTrue(results[0]["result"]["estimated"])

    def test_missing_stock_blocks_consumption_without_partial_deduction(self):
        plan = self.app.tool("recipe_plan", {"recipe": "tomato-rice", "servings": 12})
        before = self.app.snapshot()["inventory"]
        with self.assertRaises(AppError):
            self.app.complete_meal(plan["id"])
        self.assertEqual(before, self.app.snapshot()["inventory"])

    def test_multilingual_train_clarification_and_duplicate_messages(self):
        for language, text in [("ta", "ரயில் நிலை"), ("ml", "ട്രെയിൻ നില"),
                               ("kn", "ರೈಲು ಸ್ಥಿತಿ"), ("hi", "ट्रेन की स्थिति")]:
            with self.subTest(language=language):
                session = "session-" + language
                response = self.app.message(text, language, session, "m1")
                self.assertEqual(response["task"]["status"], "needs_input")
                self.assertEqual(response["language"], language)
                followup = self.app.message("12627 2026-11-01", language, session, "m2")
                self.assertEqual(followup["task"]["status"], "succeeded")
                self.assertEqual(followup["task"]["result"]["mode"], "fixture")
                again = self.app.message("12627 2026-11-01", language, session, "m2")
                self.assertEqual(followup, again)

    def test_unknown_train_is_not_fabricated(self):
        result = self.app.tool("train_status", {"train_number": "99999", "date": "2026-11-01"})
        self.assertEqual(result["status"], "failed")
        self.assertNotIn("position", result["result"])

    def test_booking_cancel_cannot_later_be_approved(self):
        task = self.app.tool("booking_preview", {
            "origin": "Chennai", "destination": "Bengaluru", "date": "2026-11-01"})
        self.app.cancel(task["id"])
        with self.assertRaises(AppError):
            self.app.approve(task["id"])

    def test_recipe_customization_and_suggestions_do_not_deduct(self):
        before = self.app.snapshot()["inventory"]
        plan = self.app.tool("recipe_plan", {
            "recipe": "tomato-rice", "servings": 4, "less_spicy": True})
        self.assertEqual(plan["result"]["servings"], 4)
        self.assertIn("less", " ".join(plan["result"]["steps"]).lower())
        self.app.tool("dish_suggestions", {})
        self.assertEqual(before, self.app.snapshot()["inventory"])

    def test_correction_reference_replay_and_conflicting_payload(self):
        first = self.app.correct_stock("rice", 500, "g", "correction-1")
        self.app.import_receipt("Rice,1,kg", "later-bill")
        self.assertEqual(self.app.correct_stock("rice", 500, "g", "correction-1"), first)
        with self.assertRaises(AppError):
            self.app.correct_stock("rice", 100, "g", "correction-1")

    def test_invalid_tool_types_are_public_validation_errors(self):
        for name, args in [([], {}), ("recipe_plan", {"recipe": "dal", "language": []})]:
            with self.assertRaises(AppError):
                self.app.tool(name, args)

    def test_less_spicy_reduces_chilli_even_for_a_single_chilli_recipe(self):
        normal = self.app.tool("recipe_plan", {"recipe": "dal", "servings": 2})
        mild = self.app.tool("recipe_plan", {"recipe": "dal", "servings": 2, "less_spicy": True})
        normal_chilli = next(i["quantity"] for i in normal["result"]["ingredients"] if i["name"] == "chilli")
        mild_chilli = next(i["quantity"] for i in mild["result"]["ingredients"] if i["name"] == "chilli")
        self.assertEqual(mild_chilli, normal_chilli / 2)

    def test_unknown_dish_is_clarified_instead_of_replaced(self):
        first = self.app.message("Cook biryani for 2", "en", "unknown-dish", "one")
        self.assertEqual(first["task"]["status"], "needs_input")
        self.assertNotIn("ingredients", first["task"]["result"])
        second = self.app.message("dal for 2", "en", "unknown-dish", "two")
        self.assertEqual(second["task"]["id"], first["task"]["id"])
        self.assertEqual(second["task"]["result"]["recipe"], "dal")


if __name__ == "__main__":
    unittest.main()
