import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from home_agent.errors import AppError
from home_agent.service import HomeAgent
from home_agent.trains import TrainFeed

STAMP = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def report(**updates):
    data = {"trainNumber": "12069", "trainName": "JANSHATABDI EXP", "startDate": "2026-10-26",
            "status": "running", "delayMinutes": 9, "lastUpdatedAt": STAMP.isoformat(),
            "isLive": True, "trackingMode": "real-time", "currentLocation": {"stationCode": "DURG", "isActualPosition": True},
            "nextHalt": {"stationCode": "R", "stationName": "Raipur"},
            "route": [{"stationCode": "DURG", "stationName": "Durg Junction"}]}
    data.update(updates)
    return {"success": True, "data": data}


class TrainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.environment = patch.dict("os.environ", {"HOME_AGENT_TRAIN_PROVIDER": "railradar", "RAILRADAR_API_KEY": "synthetic-key"})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def feed(self, payload=None):
        return TrainFeed(fetcher=lambda number, date, key: payload or report(), clock=lambda: STAMP)

    def test_recent_provider_report_has_source_and_both_timestamps(self):
        result = self.feed().lookup("12069", "2026-10-26", "en")
        self.assertEqual(result["mode"], "live")
        self.assertEqual(result["reported_station"], "Durg Junction (DURG)")
        self.assertEqual(result["delay_minutes"], 9)
        self.assertEqual(result["provider_updated_at"], STAMP.isoformat())
        self.assertIn("RailRadar", result["source"])
        self.assertIn("retrieved_at", result)

    def test_stale_missing_or_estimated_report_is_never_labeled_live(self):
        for changes in [
            {"lastUpdatedAt": (STAMP-timedelta(hours=2)).isoformat()},
            {"lastUpdatedAt": None}, {"isLive": False}, {"trackingMode": "estimated"},
            {"currentLocation": {"stationCode": "DURG", "isActualPosition": False}},
            {"lastUpdatedAt": (STAMP+timedelta(hours=2)).isoformat()},
        ]:
            with self.subTest(changes=changes):
                self.assertNotEqual(self.feed(report(**changes)).lookup("12069", "2026-10-26")["mode"], "live")

    def test_mismatched_train_or_date_and_malformed_data_are_rejected(self):
        for payload in [report(trainNumber="12627"), report(startDate="2026-10-25"), {"success": True, "data": []}, report(delayMinutes=True)]:
            with self.subTest(payload=payload):
                with self.assertRaises(AppError):
                    self.feed(payload).lookup("12069", "2026-10-26")

    def test_provider_failure_never_falls_back_to_fixture(self):
        def broken(*args):
            raise AppError("Provider is unavailable", 503, "TRAIN_PROVIDER_UNAVAILABLE")
        app = HomeAgent(Path(self.temp.name)/"test.sqlite3", train_feed=TrainFeed(fetcher=broken, clock=lambda: STAMP))
        with self.assertRaises(AppError) as error:
            app.tool("train_status", {"train_number": "12627", "date": "2026-10-26"})
        self.assertEqual(error.exception.code, "TRAIN_PROVIDER_UNAVAILABLE")
        self.assertEqual(app.snapshot()["tasks"], [])

    def test_direct_tool_and_localized_summary_use_same_provider(self):
        app = HomeAgent(Path(self.temp.name)/"test.sqlite3", train_feed=self.feed())
        result = app.tool("train_status", {"train_number": "12069", "date": "2026-10-26", "language": "ta"})
        self.assertEqual(result["result"]["mode"], "live")
        self.assertIn("12069", result["result"]["summary"])
        self.assertIn("தாமதம்", result["result"]["summary"])

    def test_repeated_lookup_is_cached_and_rechecks_freshness(self):
        calls, clock = [], [STAMP]
        def fetch(*args):
            calls.append(args)
            return report(lastUpdatedAt=(STAMP-timedelta(minutes=14)).isoformat())
        feed = TrainFeed(fetcher=fetch, clock=lambda: clock[0])
        self.assertEqual(feed.lookup("12069", "2026-10-26")["mode"], "live")
        clock[0] += timedelta(seconds=90)
        self.assertEqual(feed.lookup("12069", "2026-10-26")["mode"], "stale")
        self.assertEqual(len(calls), 1)

    def test_missing_key_and_future_date_do_not_call_provider(self):
        with patch.dict("os.environ", {"RAILRADAR_API_KEY": ""}):
            with self.assertRaises(AppError) as error:
                self.feed().lookup("12069", "2026-10-26")
        self.assertEqual(error.exception.code, "TRAIN_NOT_CONFIGURED")
        with self.assertRaises(AppError):
            self.feed().lookup("12069", "2026-10-27")
