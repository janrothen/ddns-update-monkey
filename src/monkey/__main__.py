import logging
import sys

import requests

from monkey.config import config, env, project_root
from monkey.duck_dns_client import DuckDnsClient
from monkey.duck_dns_updater import DuckDnsUpdater
from monkey.ip_resolver import IpResolver
from monkey.state_store import StateStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    stream=sys.stdout,
)


def build_updater() -> DuckDnsUpdater:
    cfg = config()
    ip_resolver = IpResolver(
        service_url=cfg["ip"]["service_url"],
        timeout=cfg["ip"]["request_timeout"],
    )
    state_store = StateStore(path=project_root() / cfg["files"]["state"])
    client = DuckDnsClient(
        update_url=cfg["duckdns"]["update_url"],
        domain=env("DUCKDNS_DOMAIN"),
        token=env("DUCKDNS_TOKEN"),
        timeout=cfg["duckdns"]["request_timeout"],
    )
    return DuckDnsUpdater(ip_resolver, state_store, client)


def main() -> None:
    try:
        build_updater().run()
    except (RuntimeError, ValueError, requests.RequestException) as e:
        logging.error("%s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
