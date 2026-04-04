from unittest.mock import patch

import pytest
import requests

from monkey.__main__ import main


def test_main_success():
    with patch("monkey.__main__.DuckDnsUpdater") as MockUpdater:
        MockUpdater.return_value.run.return_value = None
        main()  # should not raise or exit


def test_main_exits_on_runtime_error():
    with patch("monkey.__main__.DuckDnsUpdater") as MockUpdater:
        MockUpdater.return_value.run.side_effect = RuntimeError("boom")
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_exits_on_value_error():
    with patch("monkey.__main__.DuckDnsUpdater") as MockUpdater:
        MockUpdater.return_value.run.side_effect = ValueError("bad value")
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_exits_on_request_exception():
    with patch("monkey.__main__.DuckDnsUpdater") as MockUpdater:
        MockUpdater.return_value.run.side_effect = requests.RequestException("network")
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
