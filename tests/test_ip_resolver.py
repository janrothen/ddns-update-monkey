from unittest.mock import MagicMock, patch

import pytest
import requests


def test_get_success(ip_resolver):
    mock_resp = MagicMock(text="5.6.7.8\n")
    with patch("requests.get", return_value=mock_resp):
        assert ip_resolver.get() == "5.6.7.8"


def test_get_invalid_response(ip_resolver):
    """Non-IP responses from the IP service should raise ValueError."""
    mock_resp = MagicMock(text="<html>error</html>")
    with (
        patch("requests.get", return_value=mock_resp),
        pytest.raises(ValueError, match="unexpected value"),
    ):
        ip_resolver.get()


def test_get_rejects_out_of_range_octets(ip_resolver):
    """Octet values above 255 must be rejected."""
    mock_resp = MagicMock(text="999.999.999.999\n")
    with (
        patch("requests.get", return_value=mock_resp),
        pytest.raises(ValueError, match="unexpected value"),
    ):
        ip_resolver.get()


def test_get_http_error(ip_resolver):
    http_err = requests.HTTPError(response=MagicMock(status_code=503))
    with (
        patch("requests.get", side_effect=http_err),
        pytest.raises(requests.HTTPError, match="503"),
    ):
        ip_resolver.get()


def test_get_connection_error(ip_resolver):
    with (
        patch("requests.get", side_effect=requests.ConnectionError("timeout")),
        pytest.raises(requests.RequestException, match="IP service"),
    ):
        ip_resolver.get()
