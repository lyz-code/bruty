"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import json
import logging
import re
from contextlib import suppress
from typing import Any, Dict, List, Optional

from rich.progress import track
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

log = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def bruteforce(
    base_url: str,
    uris: Optional[List[str]] = None,
    uris_file_path: Optional[str] = None,
    not_found_regexp: Optional[str] = None,
    verbose: bool = False,
    ignore_status_code: bool = False,
) -> List[str]:
    """Return the urls that exist.

    Args:
        base_url: The domain to test.
        uris_file_path: Path to the file containing the uris to test.

    Returns:
        List of urls that exist.
    """
    opts = Options()
    opts.binary_location = "/usr/bin/chromium"
    opts.add_argument("--headless")
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    driver = webdriver.Chrome(options=opts, desired_capabilities=capabilities)

    existent_urls = []
    uris_to_test = []
    if uris_file_path is not None:
        with open(uris_file_path, "r") as file_descriptor:
            uris_to_test.extend(
                [
                    line
                    for line in file_descriptor.read().splitlines()
                    if not re.match(r"^#.*", line)
                ]
            )
    if uris is not None:
        uris_to_test.extend(uris)

    for uri in track(uris_to_test, description=f"Testing {len(uris_to_test)} urls..."):
        starting_url = f"{base_url}/{uri}"
        driver.get(starting_url)
        url = driver.current_url

        if not_found_regexp is not None and re.search(
            not_found_regexp, driver.page_source
        ):
            continue

        logs = driver.get_log("performance")

        if not ignore_status_code:
            try:
                status_code = get_status(url, logs)
                if status_code != 200:
                    continue
            except ValueError as e:
                if starting_url == url:
                    log.error(e)
                else:
                    log.error(f"{e}, redirected from {starting_url}")
                continue

        if verbose:
            if url != starting_url:
                log.debug(f"Redirect: {starting_url} -> {url}")
            else:
                log.debug(url)

        existent_urls.append(url)

    driver.close()
    return existent_urls


def get_status(url: str, logs: List[Dict[str, Any]]) -> int:
    """Get the url response status code.

    Args:
        url: url to search
        logs: Browser driver logs
    Returns:
        The status code.
    """
    for log in logs:
        if log["message"]:
            data = json.loads(log["message"])
            with suppress(KeyError):
                if data["message"]["params"]["response"]["url"] == url:
                    return data["message"]["params"]["response"]["status"]
    raise ValueError(f"Error retrieving the status code for url {url}")
