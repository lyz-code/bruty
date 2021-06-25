"""Tests the service layer."""

import logging

import pytest
from _pytest.logging import LogCaptureFixture

from bruty import bruteforce


@pytest.mark.usefixtures("_server")
def test_bruty_follows_redirections() -> None:
    """
    Given: A uri that redirects to `/existent` which is a 200
    When: The bruteforce service is called
    Then: The 200 endpoint is registered
    """
    result = bruteforce("http://localhost:8000", ["302_to_200"])

    assert result == ["http://localhost:8000/existent"]


@pytest.mark.usefixtures("_server")
def test_bruty_follows_redirections_to_404() -> None:
    """
    Given: A uri that redirects to `/inexistent` which is a 404
    When: The bruteforce service is called
    Then: The 404 endpoint is not registered
    """
    result = bruteforce("http://localhost:8000", ["302_to_404"])

    assert result == []


@pytest.mark.usefixtures("_server")
def test_bruty_registers_redirections_in_the_log(caplog: LogCaptureFixture) -> None:
    """
    Given: A uri that redirects to `/existent` which is a 200
    When: The bruteforce service is called in verbose mode
    Then: The redirection is registered in the logs
    """
    caplog.set_level(logging.DEBUG)

    result = bruteforce("http://localhost:8000", ["302_to_200"], verbose=True)

    assert result == ["http://localhost:8000/existent"]
    assert (
        "bruty.services",
        logging.DEBUG,
        "Redirect: http://localhost:8000/302_to_200 -> http://localhost:8000/existent",
    ) in caplog.record_tuples


@pytest.mark.usefixtures("_server")
def test_bruty_doesnt_register_redirections_to_404_in_the_log(
    caplog: LogCaptureFixture,
) -> None:
    """
    Given: A uri that redirects to `/inexistent` which is a 404
    When: The bruteforce service is called in verbose mode
    Then: The redirection is not registered in the logs
    """
    caplog.set_level(logging.DEBUG)

    result = bruteforce("http://localhost:8000", ["302_to_404"], verbose=True)

    assert result == []
    assert (
        "bruty.services",
        logging.DEBUG,
        "Redirect: http://localhost:8000/302_to_404 -> "
        "http://localhost:8000/inexistent",
    ) not in caplog.record_tuples
