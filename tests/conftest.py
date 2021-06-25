"""Store the classes and fixtures used throughout the tests."""

from multiprocessing import Process
from typing import Generator

import pytest
import uvicorn

from .api_server import app


def run_server() -> None:
    """Command to run the fake api server."""
    uvicorn.run(app)


@pytest.fixture(name="_server", scope="session")
def _server() -> Generator[None, None, None]:
    """Start the fake api server."""
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield
    proc.kill()  # Cleanup after test
