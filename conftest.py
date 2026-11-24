"""Skip the tests and doctests that need a live CouchDB when none is reachable.

The server is the one the stores connect to by default, ``COUCHDB_URL`` or
``http://127.0.0.1:5984`` (:func:`couchdol.default_couchdb_url`), so the probe,
the tests (through the ``couchdb_url`` fixture) and the doctests all target the
same server. Only items that need it are skipped: tests requesting
``couchdb_url``, and the package's doctests (every one of them opens a store).
"""

import socket
from urllib.parse import urlsplit

import pytest
from _pytest.doctest import DoctestItem

from couchdol import default_couchdb_url


#: Port the CouchDB client connects to when the URL names none (it uses the
#: scheme's own port, as ``http.client`` does).
DEFAULT_PORTS = {"http": 80, "https": 443}


def with_scheme(url: str) -> str:
    """``url``, read as ``http://...`` when it names no scheme.

    Without one, ``urlsplit`` takes the user name (or the host) for the scheme and
    finds no host at all.

    >>> with_scheme("db.example:5984")
    'http://db.example:5984'
    >>> with_scheme("https://db.example")
    'https://db.example'
    """
    return url if "://" in url else f"http://{url}"


def probe_address(url: str) -> tuple[str, int]:
    """The ``(host, port)`` the CouchDB client connects to for ``url``.

    A URL without a scheme is read as ``http://``. A port that is not a number
    raises ``ValueError``.

    >>> probe_address("https://couch.example.com")
    ('couch.example.com', 443)
    >>> probe_address("http://127.0.0.1:5984")
    ('127.0.0.1', 5984)
    >>> probe_address("couch.example.com:5984")
    ('couch.example.com', 5984)
    """
    parsed = urlsplit(with_scheme(url))
    port = parsed.port or DEFAULT_PORTS.get(parsed.scheme.lower(), 5984)
    return parsed.hostname or "127.0.0.1", port


def redact_url(url: str) -> str:
    """``url`` without its userinfo, so it can be printed (a skip reason, a log).

    A URL without a scheme is read as ``http://``, so its userinfo is found too.

    >>> redact_url("http://user:pw@couch.example.com:5984/db")
    'http://couch.example.com:5984/db'
    """
    parsed = urlsplit(with_scheme(url))
    return parsed._replace(netloc=parsed.netloc.rpartition("@")[2]).geturl()


def couchdb_reachable(url: str, *, timeout: float = 0.5) -> bool:
    """True if something accepts TCP connections at the CouchDB ``url``."""
    try:
        with socket.create_connection(probe_address(url), timeout=timeout):
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
    try:
        if couchdb_reachable(url):
            return
        reason = f"no CouchDB reachable at {redact_url(url)}"
    except ValueError:  # a malformed URL, such as a port that is not a number
        reason = f"invalid CouchDB URL {redact_url(url)}"
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if _needs_couchdb(item):
            item.add_marker(skip)
