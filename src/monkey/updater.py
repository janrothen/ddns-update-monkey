"""DuckDNS updater — fetches current public IP and updates DuckDNS if it changed."""

import json
import logging
import os
from pathlib import Path

import requests

from monkey.config import ConfigDict, config, env, project_root

log = logging.getLogger(__name__)


class DuckDNSUpdater:
    def __init__(self) -> None:
        self.token: str = env("DUCKDNS_TOKEN")
        self.domain: str = env("DUCKDNS_DOMAIN")
        self.state_file: Path = project_root() / config()["files"]["state"]
        self.last_ip: str = self._load_state()

    def _load_state(self) -> str:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text()).get("last_ip", "")
            except json.JSONDecodeError:
                log.warning("state.json is corrupt — treating as empty")
                return ""
        return ""

    def _save_state(self) -> None:
        state = {"last_ip": self.last_ip}
        # Write to a temp file first, then atomically replace the real state file.
        # os.replace() is POSIX-atomic: the old file is never left partially overwritten,
        # so a crash or disk-full error between post and save can't corrupt state.json.
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state))
        os.replace(tmp, self.state_file)

    def _get_public_ip(self) -> str:
        try:
            resp = requests.get(
                config()["ip"]["service_url"],
                timeout=config()["ip"]["request_timeout"],
            )
            resp.raise_for_status()
            return resp.text.strip()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"IP service returned HTTP {e.response.status_code}"
            ) from e
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to reach IP service: {e}") from e

    def _update_duckdns(self, ip: str) -> None:
        url = (
            f"{config()['duckdns']['update_url']}"
            f"?domains={self.domain}&token={self.token}&ip={ip}"
        )
        try:
            resp = requests.get(url, timeout=config()["duckdns"]["request_timeout"])
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"DuckDNS returned HTTP {e.response.status_code}"
            ) from e
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to reach DuckDNS: {e}") from e
        if resp.text.strip() != "OK":
            raise ValueError(f"DuckDNS returned unexpected response: {resp.text.strip()!r}")

    def run(self) -> None:
        current_ip = self._get_public_ip()

        if current_ip == self.last_ip:
            log.info("IP unchanged (%s) — no update needed", current_ip)
            return

        log.info("IP changed: %s → %s", self.last_ip or "<none>", current_ip)
        self._update_duckdns(current_ip)
        self.last_ip = current_ip
        self._save_state()  # only persisted after a successful update
        log.info("DuckDNS updated: %s → %s", self.domain, current_ip)
