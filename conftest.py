"""Skip tests and doctests that need a live CouchDB when none is reachable."""

import os
import socket
from urllib.parse import urlparse

import pytest

COUCHDB_URL = os.environ.get("COUCHDB_URL", "http://127.0.0.1:5984")


def couchdb_reachable(url: str = COUCHDB_URL, *, timeout: float = 0.5) -> bool:
    """True if something accepts TCP connections at the CouchDB ``url``."""
    parsed = urlparse(url)
    try:
        with socket.create_connection(
            (parsed.hostname or "127.0.0.1", parsed.port or 5984), timeout=timeout
        ):
            return True
    except OSError:
        return False


def pytest_collection_modifyitems(config, items):
    if couchdb_reachable():
        return
    skip = pytest.mark.skip(reason=f"no CouchDB reachable at {COUCHDB_URL}")
    for item in items:
        item.add_marker(skip)
