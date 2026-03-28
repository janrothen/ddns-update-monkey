import os
import tomllib
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

type ConfigDict = dict[str, Any]

# src/monkey/config.py → project root is two levels up
_PROJECT_ROOT = Path(__file__).parent.parent.parent

load_dotenv(_PROJECT_ROOT / ".env")


def _load():
    with open(_PROJECT_ROOT / "config.toml", "rb") as f:
        return tomllib.load(f)


_config = _load()


def config() -> ConfigDict:
    return _config


def project_root() -> Path:
    return _PROJECT_ROOT


def env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value
