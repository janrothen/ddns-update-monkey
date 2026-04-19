import pytest

from monkey.duck_dns_client import DuckDnsClient
from monkey.ip_resolver import IpResolver
from monkey.state_store import StateStore


@pytest.fixture
def ip_resolver():
    return IpResolver(service_url="https://ipv4.icanhazip.com", timeout=10)


@pytest.fixture
def state_store(tmp_path):
    return StateStore(path=tmp_path / "state.json")


@pytest.fixture
def duck_dns_client():
    return DuckDnsClient(
        update_url="https://www.duckdns.org/update",
        domain="test-domain",
        token="test-token",
        timeout=10,
    )
