import tempfile
import unittest
from pathlib import Path

from google.api_core.exceptions import NotFound, PreconditionFailed

from home_agent.cloud_state import VisitorState
from home_agent.errors import AppError


class Blob:
    def __init__(self, bucket, name):
        self.bucket, self.name = bucket, name
        self.generation, self.size = None, None

    def reload(self, **kwargs):
        if self.name not in self.bucket.objects:
            raise NotFound("missing")
        self.generation, data = self.bucket.objects[self.name]
        self.size = len(data)

    def download_to_filename(self, filename, if_generation_match, **kwargs):
        generation, data = self.bucket.objects[self.name]
        if generation != if_generation_match:
            raise PreconditionFailed("changed")
        Path(filename).write_bytes(data)

    def upload_from_filename(self, filename, if_generation_match, **kwargs):
        current = self.bucket.objects.get(self.name, (0, b""))[0]
        if self.bucket.conflict or current != if_generation_match:
            raise PreconditionFailed("changed")
        self.bucket.objects[self.name] = (current+1, Path(filename).read_bytes())


class Bucket:
    def __init__(self):
        self.objects, self.conflict = {}, False

    def blob(self, name):
        return Blob(self, name)


class CloudStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = VisitorState(root=Path(self.temp.name), bucket="")
        self.store.bucket = Bucket()
        self.token = "b"*64

    def tearDown(self):
        self.temp.cleanup()

    def test_generation_guarded_save_survives_new_temporary_database(self):
        with self.store.open(self.token, write=True) as agent:
            agent.correct_stock("rice", 123, "g", "one")
        with self.store.open(self.token) as agent:
            rice = next(i for i in agent.snapshot()["inventory"] if i["name"] == "rice")
            self.assertEqual(rice["quantity"], 123)
        self.assertEqual(len(self.store.bucket.objects), 1)

    def test_failed_save_never_reports_success_or_overwrites_old_state(self):
        with self.store.open(self.token, write=True) as agent:
            agent.correct_stock("rice", 123, "g", "one")
        self.store.bucket.conflict = True
        with self.assertRaises(AppError) as error:
            with self.store.open(self.token, write=True) as agent:
                agent.correct_stock("rice", 999, "g", "two")
        self.assertEqual(error.exception.status, 409)
        self.store.bucket.conflict = False
        with self.store.open(self.token) as agent:
            self.assertEqual(next(i["quantity"] for i in agent.snapshot()["inventory"] if i["name"] == "rice"), 123)

    def test_exception_during_action_does_not_commit_snapshot(self):
        with self.store.open(self.token) as agent:
            before = agent.snapshot()["inventory"]
        with self.assertRaises(AppError):
            with self.store.open(self.token, write=True) as agent:
                agent.correct_stock("rice", 999, "g", "rollback")
                raise AppError("abort")
        with self.store.open(self.token) as agent:
            self.assertEqual(agent.snapshot()["inventory"], before)

    def test_invalid_cookie_cannot_select_object_paths(self):
        with self.assertRaises(AppError):
            with self.store.open("../../another"):
                pass
