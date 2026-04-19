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
        # Write to a temp file first, then atomically replace the real state file.
        # os.replace() is POSIX-atomic: the old file is never left partially overwritten,
        # so a crash or disk-full error between post and save can't corrupt state.json.
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"last_ip": ip}))
        os.replace(tmp, self.path)
