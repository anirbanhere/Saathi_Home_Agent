"""Visitor-isolated SQLite snapshots, durably saved with Cloud Storage CAS.

Only local demo tools run inside this boundary. External irreversible actions
need a transactional operation store, not snapshot-based retries.
"""
import hashlib
import os
import re
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path

from .errors import AppError
from .service import HomeAgent


class VisitorState:
    def __init__(self, root=None, bucket=None):
        self.root = Path(root or os.environ.get("HOME_AGENT_VISITOR_DIR", "data/visitors"))
        self.bucket_name = os.environ.get("HOME_AGENT_STATE_BUCKET", "") if bucket is None else bucket
        self.locks = [threading.RLock() for _ in range(32)]
        self.bucket = None
        if self.bucket_name:
            from google.cloud import storage
            self.bucket = storage.Client().bucket(self.bucket_name)
        else:
            self.root.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def open(self, token, write=False):
        if not isinstance(token, str) or not re.fullmatch(r"[a-f0-9]{64}", token):
            raise AppError("Invalid visitor session.", 403, "FORBIDDEN")
        identifier = hashlib.sha256(token.encode()).hexdigest()
        with self.locks[int(identifier[:4], 16) % len(self.locks)]:
            with tempfile.TemporaryDirectory(prefix="home-agent-") as directory:
                path = Path(directory) / "state.sqlite3"
                fresh, generation, blob = True, 0, None
                if self.bucket:
                    from google.api_core.exceptions import NotFound, PreconditionFailed
                    blob = self.bucket.blob("visitors/" + identifier + ".sqlite3")
                    try:
                        blob.reload(timeout=20)
                        if blob.size > 5_000_000:
                            raise AppError("This demo workspace has reached its storage limit.", 429, "WORKSPACE_LIMIT")
                        generation = int(blob.generation)
                        blob.download_to_filename(str(path), if_generation_match=generation, timeout=20)
                        fresh = False
                    except NotFound:
                        pass
                    except PreconditionFailed:
                        raise AppError("Workspace changed. Refresh and retry.", 409, "CONFLICT") from None
                else:
                    stored = self.root / (identifier + ".sqlite3")
                    if stored.exists():
                        path.write_bytes(stored.read_bytes())
                        fresh = False
                agent = HomeAgent(path)
                yield agent
                if write or fresh:
                    if path.stat().st_size > 5_000_000:
                        raise AppError("This demo workspace has reached its storage limit.", 429, "WORKSPACE_LIMIT")
                    if blob is not None:
                        try:
                            blob.upload_from_filename(str(path), content_type="application/octet-stream",
                                                      if_generation_match=generation, timeout=30)
                        except PreconditionFailed:
                            raise AppError("Another request updated this workspace. Refresh and retry.", 409, "CONFLICT") from None
                    else:
                        # Local development uses one process; production uses the GCS generation guard.
                        destination = self.root / (identifier + ".sqlite3")
                        staged = destination.with_suffix(".pending")
                        staged.write_bytes(path.read_bytes())
                        os.replace(staged, destination)
