"""Orchestrates a DuckDNS update: resolve IP, compare to stored IP, update if changed."""

import logging

from monkey.duck_dns_client import DuckDnsClient
from monkey.ip_resolver import IpResolver
from monkey.state_store import StateStore

log = logging.getLogger(__name__)


class DuckDnsUpdater:
    def __init__(
        self,
        ip_resolver: IpResolver,
        state_store: StateStore,
        client: DuckDnsClient,
    ) -> None:
        self.ip_resolver = ip_resolver
        self.state_store = state_store
        self.client = client

    def run(self) -> None:
        last_ip = self.state_store.load()
        current_ip = self.ip_resolver.get()

        if current_ip == last_ip:
            log.info("IP unchanged (%s) — no update needed", current_ip)
            return

        log.info("IP changed: %s → %s", last_ip or "<none>", current_ip)
        self.client.update(current_ip)
        self.state_store.save(current_ip)  # only persisted after a successful update
        log.info("DuckDNS updated: %s → %s", self.client.domain, current_ip)
