"""Config and secrets loading.

Loading is lazy: `load_config()` and `env()` do I/O only on first call
(cached thereafter), so importing this module has no side effects.
"""

import os
import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def project_root() -> Path:
    """Directory that holds config.toml and .env.

    In a checkout (editable install) the repo root is anchored to this file's
    location, so invocations from any directory work. Under a regular install
    this file lives in site-packages with no config.toml nearby — fall back to
    the current working directory, which is where the cron job runs the tool.
    """
    anchored = Path(__file__).resolve().parents[2]
    if (anchored / "config.toml").is_file():
        return anchored
    return Path.cwd()


@dataclass(frozen=True)
class Config:
    ip_service_url: str
    ip_request_timeout: int
    duckdns_update_url: str
    duckdns_request_timeout: int
    state_file: Path


@lru_cache(maxsize=1)
def load_config() -> Config:
    root = project_root()
    with open(root / "config.toml", "rb") as f:
        raw = tomllib.load(f)
    return Config(
        ip_service_url=raw["ip"]["service_url"],
        ip_request_timeout=raw["ip"]["request_timeout"],
        duckdns_update_url=raw["duckdns"]["update_url"],
        duckdns_request_timeout=raw["duckdns"]["request_timeout"],
        state_file=root / raw["files"]["state"],
    )


@lru_cache(maxsize=1)
def _load_dotenv_once() -> None:
    load_dotenv(project_root() / ".env")


def env(key: str) -> str:
    _load_dotenv_once()
    value = os.environ.get(key)
    if not value:
        # An empty value (e.g. a bare `DUCKDNS_TOKEN=` line in .env) is as
        # useless as a missing one — fail here with a clear message instead
        # of at the API.
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value
