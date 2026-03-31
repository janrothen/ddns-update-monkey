from unittest.mock import patch

import pytest

from monkey.duck_dns_updater import DuckDnsUpdater

FAKE_CONFIG = {
    "ip": {"service_url": "https://ipv4.icanhazip.com", "request_timeout": 10},
    "duckdns": {"update_url": "https://www.duckdns.org/update", "request_timeout": 10},
    "files": {"state": "state.json"},
}

FAKE_SECRETS = {"DUCKDNS_TOKEN": "test-token", "DUCKDNS_DOMAIN": "test-domain"}


@pytest.fixture
def updater(tmp_path):
    with (
        patch("monkey.duck_dns_updater.env", side_effect=FAKE_SECRETS.__getitem__),
        patch("monkey.duck_dns_updater.config", return_value=FAKE_CONFIG),
        patch("monkey.duck_dns_updater.project_root", return_value=tmp_path),
    ):
        yield DuckDnsUpdater()
