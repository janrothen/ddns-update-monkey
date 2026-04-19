"""Resolves the host's current public IPv4 address via an HTTP echo service."""

import ipaddress

import requests


class IpResolver:
    def __init__(self, service_url: str, timeout: int) -> None:
        self.service_url = service_url
        self.timeout = timeout

    def get(self) -> str:
        try:
            resp = requests.get(self.service_url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"IP service returned HTTP {e.response.status_code}"
            ) from e
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to reach IP service: {e}") from e

        ip = resp.text.strip()
        try:
            ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"IP service returned unexpected value: {ip!r}") from e
        return ip
