import logging
import sys

import requests

from monkey.updater import DuckDNSUpdater

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    try:
        DuckDNSUpdater().run()
    except (RuntimeError, ValueError, requests.RequestException) as e:
        logging.error("%s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
