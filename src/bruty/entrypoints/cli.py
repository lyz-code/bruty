"""Command line interface definition."""

from typing import List, Optional

import click

from .. import version
from ..services import bruteforce
from . import load_logger


@click.command(help="Bruteforce dynamic web applications with Selenium.")
@click.version_option(version="", message=version.version_info())
@click.argument("url")
@click.option("-f", "--uris_file_path")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-n", "--not_found_regexp")
@click.option("-u", "--uris", multiple=True)
def cli(
    url: str,
    verbose: bool = False,
    uris_file_path: Optional[str] = None,
    uris: Optional[List[str]] = None,
    not_found_regexp: Optional[str] = None,
) -> None:
    """Command line interface main click entrypoint."""
    load_logger(verbose)
    urls = bruteforce(url, uris, uris_file_path, not_found_regexp)
    for url in urls:
        print(url)


if __name__ == "__main__":  # pragma: no cover
    # E1120: As the arguments are passed through the function decorators instead of
    # during the function call, pylint get's confused.
    cli(ctx={})  # noqa: E1120
