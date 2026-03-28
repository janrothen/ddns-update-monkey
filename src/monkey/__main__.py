import logging
import sys

import requests

from monkey.duck_dns_updater import DuckDnsUpdater

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    try:
        DuckDnsUpdater().run()
    except (RuntimeError, ValueError, requests.RequestException) as e:
        logging.error("%s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
