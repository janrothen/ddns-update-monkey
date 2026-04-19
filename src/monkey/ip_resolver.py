"""Resolves the host's current public IPv4 address via an HTTP echo service."""

import ipaddress

from monkey import _http


class IpResolver:
    def __init__(self, service_url: str, timeout: int) -> None:
        self.service_url = service_url
        self.timeout = timeout

    def get(self) -> str:
        resp = _http.get(self.service_url, "IP service", self.timeout)
        ip = resp.text.strip()
        try:
            ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"IP service returned unexpected value: {ip!r}") from e
        return ip
