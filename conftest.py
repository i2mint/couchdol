"""Skip the tests and doctests that need a live CouchDB when none is reachable.

The server is the one the stores connect to by default, ``COUCHDB_URL`` or
``http://127.0.0.1:5984`` (:func:`couchdol.default_couchdb_url`), so the probe,
the tests (through the ``couchdb_url`` fixture) and the doctests all target the
same server. Only items that need it are skipped: tests requesting
``couchdb_url``, and the package's doctests (every one of them opens a store).
"""

import socket
from urllib.parse import urlparse

import pytest
from _pytest.doctest import DoctestItem

from couchdol import default_couchdb_url


def couchdb_reachable(url: str, *, timeout: float = 0.5) -> bool:
    """True if something accepts TCP connections at the CouchDB ``url``."""
    parsed = urlparse(url)
    try:
        with socket.create_connection(
            (parsed.hostname or "127.0.0.1", parsed.port or 5984), timeout=timeout
        ):
            return True
    except OSError:
        return False


def _needs_couchdb(item) -> bool:
    return "couchdb_url" in getattr(item, "fixturenames", ()) or isinstance(
        item, DoctestItem
    )


@pytest.fixture
def couchdb_url() -> str:
    """The CouchDB URL the suite runs against (the one the reachability probe used)."""
    return default_couchdb_url()


def pytest_collection_modifyitems(config, items):
    url = default_couchdb_url()
    if couchdb_reachable(url):
        return
    skip = pytest.mark.skip(reason=f"no CouchDB reachable at {url}")
    for item in items:
        if _needs_couchdb(item):
            item.add_marker(skip)
