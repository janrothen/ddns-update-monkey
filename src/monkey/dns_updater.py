"""DNS updater protocol — defines the interface every provider must satisfy."""

from typing import Protocol


class DnsUpdater(Protocol):
    def run(self) -> None: ...
