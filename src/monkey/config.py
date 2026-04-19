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

# Anchor the project root to this file's location rather than `Path.cwd()`,
# so invocations from any directory still resolve config.toml and .env.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    ip_service_url: str
    ip_request_timeout: int
    duckdns_update_url: str
    duckdns_request_timeout: int
    state_file: Path


@lru_cache(maxsize=1)
def load_config() -> Config:
    with open(PROJECT_ROOT / "config.toml", "rb") as f:
        raw = tomllib.load(f)
    return Config(
        ip_service_url=raw["ip"]["service_url"],
        ip_request_timeout=raw["ip"]["request_timeout"],
        duckdns_update_url=raw["duckdns"]["update_url"],
        duckdns_request_timeout=raw["duckdns"]["request_timeout"],
        state_file=PROJECT_ROOT / raw["files"]["state"],
    )


@lru_cache(maxsize=1)
def _load_dotenv_once() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def env(key: str) -> str:
    _load_dotenv_once()
    value = os.environ.get(key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value
