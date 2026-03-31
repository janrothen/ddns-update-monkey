import os
import tomllib
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

type ConfigDict = dict[str, Any]

# Project root is the working directory — the cron job sets HOME to the project
# directory and cd's into it; manual invocation is expected from the project root.
load_dotenv(Path.cwd() / ".env")


def _load() -> ConfigDict:
    with open(Path.cwd() / "config.toml", "rb") as f:
        return tomllib.load(f)


_config = _load()


def config() -> ConfigDict:
    return _config


def project_root() -> Path:
    return Path.cwd()


def env(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value
