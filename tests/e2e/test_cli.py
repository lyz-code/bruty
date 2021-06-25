"""Test the command line interface."""

import logging
import re

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from py._path.local import LocalPath

from bruty.entrypoints.cli import cli
from bruty.version import __version__

log = logging.getLogger(__name__)


@pytest.fixture(name="runner")
def fixture_runner() -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False)


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(
        fr" *bruty version: {__version__}\n" r" *python version: .*\n *platform: .*",
        result.stdout,
    )


@pytest.mark.usefixtures("_server")
def test_bruty_accepts_endpoint_and_list_of_uris(runner: CliRunner) -> None:
    """
    Given: A file with a two uris one existent and an inexistent one
    When: The cli is called with a path to the file and the url to test
    Then: The urls are tested and the existent one is returned
    """
    uris_file_path = "tests/assets/uris.txt"

    result = runner.invoke(cli, ["http://localhost:8000", "-f", uris_file_path])

    assert result.exit_code == 0
    assert "http://localhost:8000/existent" in result.stdout
    assert "http://localhost:8000/inexistent" not in result.stdout


@pytest.mark.usefixtures("_server")
def test_bruty_doesnt_include_fake_404_pages(runner: CliRunner) -> None:
    """
    Given: A server that returns a 404 page with a 200 return code
    When: The cli is called with that url and a working one
    Then: The 404 page is not added to the resulting urls
    """
    result = runner.invoke(
        cli,
        [
            "http://localhost:8000",
            "-u",
            "existent",
            "-u",
            "wrong_404_page",
            "-n",
            "404 err.*",
        ],
    )

    assert result.exit_code == 0
    assert "http://localhost:8000/existent" in result.stdout
    assert "http://localhost:8000/wrong_404_page" not in result.stdout


def test_bruty_ignores_comments_on_uri_files(
    runner: CliRunner, tmpdir: LocalPath
) -> None:
    """
    Given: A uri file with only comments
    When: The cli is called
    Then: No url is processed but no error is shown either
    """
    uris_file_path = f"{tmpdir}/uris.txt"
    with open(uris_file_path, "w+") as file_descriptor:
        file_descriptor.write("# This is a comment")

    result = runner.invoke(cli, ["http://localhost:8000", "-f", uris_file_path])

    assert result.exit_code == 0


@pytest.mark.usefixtures("_server")
def test_bruty_verbose_shows_200_on_log(
    runner: CliRunner, caplog: LogCaptureFixture
) -> None:
    """
    Given: A uri that returns a 200
    When: The cli is called in verbose mode
    Then: The 200 uri is matched as soon as it appears.
    """
    caplog.set_level(logging.DEBUG)

    result = runner.invoke(
        cli,
        [
            "http://localhost:8000",
            "-u",
            "existent",
            "-v",
        ],
    )

    assert result.exit_code == 0
    assert "http://localhost:8000/existent" in result.stdout
    assert (
        "bruty.services",
        logging.DEBUG,
        "http://localhost:8000/existent",
    ) in caplog.record_tuples


@pytest.mark.usefixtures("_server")
def test_bruty_ignores_status_code_if_asked(runner: CliRunner) -> None:
    """
    Given: A uri that returns a 999 status code
    When: The cli is called with ignore_status_code
    Then: The 999 uri is registered.

    This flag is interesting for websites so broken that the status codes should
    not be trusted. It only makes sense to use in conjunction with the 404 regexp.
    """
    result = runner.invoke(
        cli,
        [
            "http://localhost:8000",
            "-u",
            "status_code_999",
            "-i",
        ],
    )

    assert result.exit_code == 0
    assert "http://localhost:8000/status_code_999" in result.stdout
