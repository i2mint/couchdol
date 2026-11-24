"""The CouchDB reachability probe in the root ``conftest.py``: port and printable URL."""

import socket

import pytest

import conftest

USERINFO_URL = "http://alice:not-a-secret@db.invalid:5984/"  # fake credentials
SCHEMELESS_URL = "alice:not-a-secret@db.invalid:5984/db"  # fake credentials, no scheme


@pytest.mark.parametrize(
    "url, address",
    [
        ("https://couch.example.com", ("couch.example.com", 443)),
        ("http://couch.example.com", ("couch.example.com", 80)),
        ("https://couch.example.com:6984", ("couch.example.com", 6984)),
        ("http://127.0.0.1:5984", ("127.0.0.1", 5984)),
        (USERINFO_URL, ("db.invalid", 5984)),
        (SCHEMELESS_URL, ("db.invalid", 5984)),
        ("db.invalid:5984", ("db.invalid", 5984)),
    ],
)
def test_probe_connects_where_the_client_does(url, address, monkeypatch):
    calls = []

    def fake_connect(addr, timeout=None):
        calls.append(addr)
        raise OSError

    monkeypatch.setattr(socket, "create_connection", fake_connect)
    assert not conftest.couchdb_reachable(url)
    assert calls == [address]


class _Item:
    fixturenames = ("couchdb_url",)

    def __init__(self):
        self.markers = []

    def add_marker(self, marker):
        self.markers.append(marker)


def _skip_reason(monkeypatch, url):
    monkeypatch.setattr(conftest, "default_couchdb_url", lambda: url)
    item = _Item()
    conftest.pytest_collection_modifyitems(None, [item])
    (reason,) = [m.kwargs["reason"] for m in item.markers]
    return reason


@pytest.mark.parametrize("url", [USERINFO_URL, SCHEMELESS_URL])
def test_skip_reason_does_not_print_credentials(url, monkeypatch):
    monkeypatch.setattr(conftest, "couchdb_reachable", lambda url: False)
    reason = _skip_reason(monkeypatch, url)
    assert "not-a-secret" not in reason and "alice" not in reason
    assert "db.invalid:5984" in reason


@pytest.mark.parametrize("url", [USERINFO_URL, SCHEMELESS_URL])
def test_redact_url_drops_the_userinfo(url):
    redacted = conftest.redact_url(url)
    assert "not-a-secret" not in redacted and "alice" not in redacted
    assert redacted.startswith("http://db.invalid:5984/")


def test_a_malformed_port_skips_with_a_redacted_reason(monkeypatch):
    """A bad port is a skip, not a collection error, and keeps credentials out."""
    reason = _skip_reason(monkeypatch, "http://alice:not-a-secret@db.invalid:abc/")
    assert "not-a-secret" not in reason and "alice" not in reason
    assert "db.invalid:abc" in reason


def test_persister_adds_a_scheme_to_a_schemeless_url(monkeypatch):
    """Credentials go into a well-formed ``http://`` URL when ``url`` names no scheme."""
    import couchdol

    urls = []

    class FakeServer(dict):
        def __init__(self, url, **kwargs):
            urls.append(url)

        def create(self, name):
            self[name] = {}

    monkeypatch.setattr(couchdol, "Server", FakeServer)
    couchdol.CouchDbPersister(user="u", password="p", url="db.invalid:5984")
    assert urls == ["http://u:p@db.invalid:5984"]
