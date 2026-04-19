"""Thin HTTP client for the DuckDNS update endpoint."""

import requests


class DuckDnsClient:
    def __init__(
        self,
        update_url: str,
        domain: str,
        token: str,
        timeout: int,
    ) -> None:
        self.update_url = update_url
        self.domain = domain
        self.token = token
        self.timeout = timeout

    def update(self, ip: str) -> None:
        # Pass secrets via params, never string-formatted into the URL.
        # This keeps the token out of `requests` exception messages, which
        # otherwise include the full request URL (and thus the token).
        params = {"domains": self.domain, "token": self.token, "ip": ip}
        try:
            resp = requests.get(self.update_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"DuckDNS returned HTTP {e.response.status_code}"
            ) from e
        except requests.RequestException as e:
            # Do not interpolate `e` — it may embed the request URL + token.
            raise requests.RequestException("Failed to reach DuckDNS") from e
        if resp.text.strip() != "OK":
            raise ValueError(
                f"DuckDNS returned unexpected response: {resp.text.strip()!r}"
            )
