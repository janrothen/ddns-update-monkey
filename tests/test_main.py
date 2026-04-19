from unittest.mock import MagicMock, patch

import pytest
import requests

from monkey.__main__ import build_updater, main
from monkey.duck_dns_updater import DuckDnsUpdater

FAKE_CONFIG = {
    "ip": {"service_url": "https://ipv4.icanhazip.com", "request_timeout": 10},
    "duckdns": {"update_url": "https://www.duckdns.org/update", "request_timeout": 10},
    "files": {"state": "state.json"},
}
FAKE_SECRETS = {"DUCKDNS_TOKEN": "t", "DUCKDNS_DOMAIN": "d"}


def _patch_build(side_effect=None, return_value=None):
    updater = MagicMock()
    if side_effect is not None:
        updater.run.side_effect = side_effect
    else:
        updater.run.return_value = return_value
    return patch("monkey.__main__.build_updater", return_value=updater)


def test_main_success():
    with _patch_build(return_value=None):
        main()  # should not raise or exit


@pytest.mark.parametrize(
    "exc",
    [
        RuntimeError("boom"),
        ValueError("bad value"),
        requests.RequestException("network"),
    ],
)
def test_main_exits_on_known_failures(exc):
    with _patch_build(side_effect=exc), pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_build_updater_wires_collaborators(tmp_path):
    with (
        patch("monkey.__main__.config", return_value=FAKE_CONFIG),
        patch("monkey.__main__.env", side_effect=FAKE_SECRETS.__getitem__),
        patch("monkey.__main__.project_root", return_value=tmp_path),
    ):
        updater = build_updater()
    assert isinstance(updater, DuckDnsUpdater)
    assert updater.client.domain == "d"
    assert updater.client.token == "t"
    assert updater.state_store.path == tmp_path / "state.json"
    assert updater.ip_resolver.service_url == "https://ipv4.icanhazip.com"
