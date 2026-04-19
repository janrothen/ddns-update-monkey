from pathlib import Path

import pytest

from monkey import config as config_module
from monkey.config import Config, env, load_config


def test_env_returns_value(monkeypatch):
    monkeypatch.setenv("SOME_KEY", "hello")
    assert env("SOME_KEY") == "hello"


def test_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("SOME_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SOME_KEY"):
        env("SOME_KEY")


def test_env_loads_dotenv_once(monkeypatch):
    """`load_dotenv` must be invoked on first env() call, and only once."""
    calls = []
    monkeypatch.setattr(config_module, "load_dotenv", lambda path: calls.append(path))
    config_module._load_dotenv_once.cache_clear()
    monkeypatch.setenv("SOME_KEY", "v")

    env("SOME_KEY")
    env("SOME_KEY")

    assert len(calls) == 1
    assert calls[0] == config_module.PROJECT_ROOT / ".env"


def test_load_config_parses_toml(tmp_path, monkeypatch):
    (tmp_path / "config.toml").write_text(
        """
        [ip]
        service_url = "https://example/ip"
        request_timeout = 7

        [duckdns]
        update_url = "https://example/update"
        request_timeout = 11

        [files]
        state = "state.json"
        """
    )
    monkeypatch.setattr(config_module, "PROJECT_ROOT", tmp_path)
    load_config.cache_clear()

    cfg = load_config()

    assert isinstance(cfg, Config)
    assert cfg.ip_service_url == "https://example/ip"
    assert cfg.ip_request_timeout == 7
    assert cfg.duckdns_update_url == "https://example/update"
    assert cfg.duckdns_request_timeout == 11
    assert cfg.state_file == tmp_path / "state.json"


def test_project_root_points_at_repo():
    """The anchor must resolve to the repo root, not the cwd."""
    assert (config_module.PROJECT_ROOT / "pyproject.toml").is_file()
    assert Path(config_module.__file__).resolve() == (
        config_module.PROJECT_ROOT / "src" / "monkey" / "config.py"
    )
