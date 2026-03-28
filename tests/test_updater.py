import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from monkey.duck_dns_updater import DuckDnsUpdater

_FAKE_CONFIG = {
    "ip": {"service_url": "https://ipv4.icanhazip.com", "request_timeout": 10},
    "duckdns": {"update_url": "https://www.duckdns.org/update", "request_timeout": 10},
    "files": {"state": "state.json"},
}

_FAKE_SECRETS = {"DUCKDNS_TOKEN": "test-token", "DUCKDNS_DOMAIN": "test-domain"}


@pytest.fixture
def updater(tmp_path):
    with (
        patch("monkey.duck_dns_updater.env", side_effect=_FAKE_SECRETS.__getitem__),
        patch("monkey.duck_dns_updater.config", return_value=_FAKE_CONFIG),
        patch("monkey.duck_dns_updater.project_root", return_value=tmp_path),
    ):
        yield DuckDnsUpdater()


# --- state -------------------------------------------------------------------

def test_load_state_missing_file(updater):
    assert updater.last_ip == ""


def test_load_state_reads_existing(updater):
    updater.state_file.write_text(json.dumps({"last_ip": "1.2.3.4"}))
    assert updater._load_state() == "1.2.3.4"


def test_load_state_corrupt_json(updater):
    updater.state_file.write_text("not json{{{")
    assert updater._load_state() == ""


def test_save_state_writes_correctly(updater):
    updater.last_ip = "1.2.3.4"
    updater._save_state()
    assert json.loads(updater.state_file.read_text()) == {"last_ip": "1.2.3.4"}


def test_save_state_is_atomic(updater):
    """Temp file must not linger after a successful save."""
    updater.last_ip = "1.2.3.4"
    updater._save_state()
    assert not updater.state_file.with_suffix(".tmp").exists()


# --- _get_public_ip ----------------------------------------------------------

def test_get_public_ip_success(updater):
    mock_resp = MagicMock()
    mock_resp.text = "5.6.7.8\n"
    with patch("requests.get", return_value=mock_resp):
        assert updater._get_public_ip() == "5.6.7.8"


def test_get_public_ip_http_error(updater):
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    http_err = requests.HTTPError(response=mock_resp)
    with patch("requests.get", side_effect=http_err):
        with pytest.raises(requests.HTTPError, match="503"):
            updater._get_public_ip()


def test_get_public_ip_connection_error(updater):
    with patch("requests.get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(requests.RequestException, match="IP service"):
            updater._get_public_ip()


# --- _update_duckdns ---------------------------------------------------------

def test_update_duckdns_success(updater):
    mock_resp = MagicMock()
    mock_resp.text = "OK"
    with patch("requests.get", return_value=mock_resp):
        updater._update_duckdns("1.2.3.4")  # should not raise


def test_update_duckdns_unexpected_response(updater):
    mock_resp = MagicMock()
    mock_resp.text = "KO"
    with patch("requests.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="unexpected response"):
            updater._update_duckdns("1.2.3.4")


def test_update_duckdns_no_token_in_error(updater):
    """HTTP errors must not leak the token into the message."""
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    http_err = requests.HTTPError(response=mock_resp)
    with patch("requests.get", side_effect=http_err):
        with pytest.raises(requests.HTTPError) as exc_info:
            updater._update_duckdns("1.2.3.4")
    assert "test-token" not in str(exc_info.value)


# --- run ---------------------------------------------------------------------

def test_run_no_update_when_ip_unchanged(updater):
    updater.last_ip = "1.2.3.4"
    mock_resp = MagicMock()
    mock_resp.text = "1.2.3.4\n"
    with patch("requests.get", return_value=mock_resp) as mock_get:
        updater.run()
    mock_get.assert_called_once()  # only the IP lookup, no DuckDNS call


def test_run_updates_and_saves_when_ip_changed(updater):
    updater.last_ip = "1.2.3.4"
    ip_resp = MagicMock(text="9.9.9.9\n")
    dns_resp = MagicMock(text="OK")
    with patch("requests.get", side_effect=[ip_resp, dns_resp]):
        updater.run()
    assert updater.last_ip == "9.9.9.9"
    assert json.loads(updater.state_file.read_text())["last_ip"] == "9.9.9.9"


def test_run_does_not_save_state_on_failed_update(updater):
    updater.last_ip = "1.2.3.4"
    ip_resp = MagicMock(text="9.9.9.9\n")
    dns_resp = MagicMock(text="KO")
    with patch("requests.get", side_effect=[ip_resp, dns_resp]):
        with pytest.raises(ValueError):
            updater.run()
    assert not updater.state_file.exists()
