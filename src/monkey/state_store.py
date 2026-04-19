"""Persists the last known public IP to disk with atomic writes."""

import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> str:
        if not self.path.exists():
            return ""
        try:
            return json.loads(self.path.read_text()).get("last_ip", "")
        except json.JSONDecodeError:
            log.warning("%s is corrupt — treating as empty", self.path.name)
            return ""

    def save(self, ip: str) -> None:
        # Durable atomic write on a Pi that can lose power mid-run:
        #   - fsync(tmp) so os.replace swaps in content that's on disk, not just
        #     in the page cache.
        #   - os.replace is metadata-atomic, so state.json is never torn.
        #   - fsync(parent dir) so the rename itself survives a power cut —
        #     otherwise the directory entry can come back empty.
        tmp = self.path.with_suffix(".tmp")
        payload = json.dumps({"last_ip": ip})
        try:
            with open(tmp, "w") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
            dir_fd = os.open(self.path.parent, os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
