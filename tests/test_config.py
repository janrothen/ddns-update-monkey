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


def test_env_raises_when_empty(monkeypatch):
    """A bare `KEY=` line in .env must not pass validation."""
    monkeypatch.setenv("SOME_KEY", "")
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
    assert calls[0] == config_module.project_root() / ".env"


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
    monkeypatch.setattr(config_module, "project_root", lambda: tmp_path)
    load_config.cache_clear()

    cfg = load_config()

    assert isinstance(cfg, Config)
    assert cfg.ip_service_url == "https://example/ip"
    assert cfg.ip_request_timeout == 7
    assert cfg.duckdns_update_url == "https://example/update"
    assert cfg.duckdns_request_timeout == 11
    assert cfg.state_file == tmp_path / "state.json"


def test_project_root_points_at_repo():
    """In a checkout, the anchor must resolve to the repo root, not the cwd."""
    config_module.project_root.cache_clear()
    try:
        root = config_module.project_root()
        assert (root / "pyproject.toml").is_file()
        assert Path(config_module.__file__).resolve() == (
            root / "src" / "monkey" / "config.py"
        )
    finally:
        config_module.project_root.cache_clear()


def test_project_root_falls_back_to_cwd(monkeypatch, tmp_path):
    """Under a regular install there is no config.toml next to the source —
    the root must fall back to the working directory the tool is run from."""
    fake_file = tmp_path / "venv" / "site-packages" / "monkey" / "config.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.touch()
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    monkeypatch.setattr(config_module, "__file__", str(fake_file))
    monkeypatch.chdir(app_dir)
    config_module.project_root.cache_clear()
    try:
        assert config_module.project_root() == app_dir
    finally:
        config_module.project_root.cache_clear()
