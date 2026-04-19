"""Internal HTTP helper.

Wraps `requests.get` with uniform exception handling. The caught exception
is never interpolated into the re-raised message — `requests` embeds the
full request URL (including query-string secrets like the DuckDNS token)
in connection-level errors, and interpolation would leak it into logs.
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
        ) from e
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to reach {service_name}") from e
    return resp
