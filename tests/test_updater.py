from unittest.mock import MagicMock

import pytest

from monkey.duck_dns_updater import DuckDnsUpdater


def _build(current_ip: str, last_ip: str = ""):
    ip_resolver = MagicMock()
    ip_resolver.get.return_value = current_ip
    state_store = MagicMock()
    state_store.load.return_value = last_ip
    client = MagicMock()
    client.domain = "test-domain"
    return (
        DuckDnsUpdater(ip_resolver, state_store, client),
        ip_resolver,
        state_store,
        client,
    )


def test_run_no_update_when_ip_unchanged():
    updater, _, state_store, client = _build(current_ip="1.2.3.4", last_ip="1.2.3.4")
    updater.run()
    client.update.assert_not_called()
    state_store.save.assert_not_called()


def test_run_updates_and_saves_when_ip_changed():
    updater, _, state_store, client = _build(current_ip="9.9.9.9", last_ip="1.2.3.4")
    updater.run()
    client.update.assert_called_once_with("9.9.9.9")
    state_store.save.assert_called_once_with("9.9.9.9")


def test_run_updates_when_no_previous_state():
    updater, _, state_store, client = _build(current_ip="9.9.9.9", last_ip="")
    updater.run()
    client.update.assert_called_once_with("9.9.9.9")
    state_store.save.assert_called_once_with("9.9.9.9")


def test_run_does_not_save_state_on_failed_update():
    updater, _, state_store, client = _build(current_ip="9.9.9.9", last_ip="1.2.3.4")
    client.update.side_effect = ValueError("boom")
    with pytest.raises(ValueError):
        updater.run()
    state_store.save.assert_not_called()
