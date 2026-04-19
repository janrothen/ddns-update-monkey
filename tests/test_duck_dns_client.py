from unittest.mock import MagicMock, patch

import pytest
import requests


def test_update_success(duck_dns_client):
    mock_resp = MagicMock(text="OK")
    with patch("requests.get", return_value=mock_resp):
        duck_dns_client.update("1.2.3.4")  # should not raise


def test_update_unexpected_response(duck_dns_client):
    mock_resp = MagicMock(text="KO")
    with (
        patch("requests.get", return_value=mock_resp),
        pytest.raises(ValueError, match="unexpected response"),
    ):
        duck_dns_client.update("1.2.3.4")


def test_update_http_error(duck_dns_client):
    http_err = requests.HTTPError(response=MagicMock(status_code=403))
    with (
        patch("requests.get", side_effect=http_err),
        pytest.raises(requests.HTTPError, match="403"),
    ):
        duck_dns_client.update("1.2.3.4")


def test_update_no_token_in_error(duck_dns_client):
    """HTTP errors must not leak the token into the message."""
    http_err = requests.HTTPError(response=MagicMock(status_code=403))
    with (
        patch("requests.get", side_effect=http_err),
        pytest.raises(requests.HTTPError) as exc_info,
    ):
        duck_dns_client.update("1.2.3.4")
    assert "test-token" not in str(exc_info.value)


def test_update_no_token_in_connection_error(duck_dns_client):
    """Connection errors carry the request URL — token must not bleed through."""
    conn_err = requests.ConnectionError(
        "HTTPSConnectionPool(host='www.duckdns.org', port=443): "
        "Max retries exceeded with url: /update?domains=test-domain"
        "&token=test-token&ip=1.2.3.4"
    )
    with (
        patch("requests.get", side_effect=conn_err),
        pytest.raises(requests.RequestException) as exc_info,
    ):
        duck_dns_client.update("1.2.3.4")
    assert "test-token" not in str(exc_info.value)


def test_update_passes_secrets_via_params(duck_dns_client):
    """Secrets must be passed via `params=`, not embedded in the URL string."""
    mock_resp = MagicMock(text="OK")
    with patch("requests.get", return_value=mock_resp) as mock_get:
        duck_dns_client.update("1.2.3.4")
    args, kwargs = mock_get.call_args
    assert args == (duck_dns_client.update_url,)
    assert kwargs["params"] == {
        "domains": "test-domain",
        "token": "test-token",
        "ip": "1.2.3.4",
    }
    assert "test-token" not in args[0]
