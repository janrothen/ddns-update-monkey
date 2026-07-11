"""Thin HTTP client for the DuckDNS update endpoint."""

from monkey import _http


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
        # The token travels as a query parameter either way — that's DuckDNS's
        # API design, and their servers see it regardless. What we control is
        # local leakage: _http scrubs exception messages, which would otherwise
        # embed the full request URL, token included.
        params = {"domains": self.domain, "token": self.token, "ip": ip}
        resp = _http.get(self.update_url, "DuckDNS", self.timeout, params=params)
        if resp.text.strip() != "OK":
            raise ValueError(
                f"DuckDNS returned unexpected response: {resp.text.strip()!r}"
            )
