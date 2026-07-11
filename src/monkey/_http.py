"""Internal HTTP helper.

Wraps `requests.get` with uniform exception handling. The caught exception
is never interpolated into the re-raised message, and the chain is severed
with `from None` — `requests` embeds the full request URL (including
query-string secrets like the DuckDNS token) in its error messages, and a
chained __cause__/__context__ would resurface it in any printed traceback.
"""

from __future__ import annotations

import requests


def get(
    url: str,
    service_name: str,
    timeout: int,
    params: dict[str, str] | None = None,
) -> requests.Response:
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(
            f"{service_name} returned HTTP {e.response.status_code}"
        ) from None
    except requests.RequestException:
        raise requests.RequestException(f"Failed to reach {service_name}") from None
    return resp
