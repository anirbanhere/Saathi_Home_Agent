import unittest

from home_agent.errors import AppError
from home_agent.model_adapters import ModelProfile
from home_agent.model_health import ModelHealth


class HealthTests(unittest.TestCase):
    def test_no_observation_then_failure_recovery_and_expiry(self):
        clock = [10.0]
        health = ModelHealth(clock=lambda: clock[0], ttl=60)
        profile = ModelProfile("openrouter", "test/model:free")
        self.assertEqual(health.status(profile)["state"], "unobserved")
        health.record(
            profile,
            error=AppError("private detail", 429, "RATE_LIMITED"),
            elapsed_ms=50,
        )
        failed = health.status(profile)
        self.assertEqual(failed["state"], "rate_limited")
        self.assertEqual(failed["elapsed_ms"], 50)
        self.assertNotIn("private detail", str(failed))
        health.record(profile, elapsed_ms=25)
        self.assertEqual(health.status(profile)["state"], "responding")
        clock[0] += 61
        self.assertEqual(health.status(profile)["state"], "stale")

    def test_profiles_are_isolated_and_cache_is_bounded(self):
        health = ModelHealth(max_entries=2)
        for model in ["a:free", "b:free", "c:free"]:
            health.record(ModelProfile("openrouter", model))
        self.assertEqual(
            health.status(ModelProfile("openrouter", "a:free"))["state"], "unobserved"
        )
        self.assertEqual(
            health.status(ModelProfile("meta", "c:free"))["state"], "unobserved"
        )
        self.assertEqual(
            health.status(ModelProfile("openrouter", "c:free"))["state"], "responding"
        )

    def test_status_is_a_model_request_observation_not_task_success(self):
        health = ModelHealth()
        profile = ModelProfile("openrouter", "a:free")
        health.record(profile)
        status = health.status(profile)
        self.assertIn("not a guarantee", status["message"])
        self.assertNotIn("task", set(status))
