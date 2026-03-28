import pytest

from monkey.config import env


def test_env_returns_value(monkeypatch):
    monkeypatch.setenv("SOME_KEY", "hello")
    assert env("SOME_KEY") == "hello"


def test_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("SOME_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SOME_KEY"):
        env("SOME_KEY")
