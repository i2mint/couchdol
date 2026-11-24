"""The CouchDB reachability probe in the root ``conftest.py``: port and printable URL."""

import socket

import pytest

import conftest

USERINFO_URL = "http://alice:not-a-secret@db.invalid:5984/"  # fake credentials


@pytest.mark.parametrize(
    "url, address",
    [
        ("https://couch.example.com", ("couch.example.com", 443)),
        ("http://couch.example.com", ("couch.example.com", 80)),
        ("https://couch.example.com:6984", ("couch.example.com", 6984)),
        ("http://127.0.0.1:5984", ("127.0.0.1", 5984)),
        (USERINFO_URL, ("db.invalid", 5984)),
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


def test_skip_reason_does_not_print_credentials(monkeypatch):
    monkeypatch.setattr(conftest, "couchdb_reachable", lambda url: False)
    monkeypatch.setattr(conftest, "default_couchdb_url", lambda: USERINFO_URL)

    class Item:
        fixturenames = ("couchdb_url",)

        def __init__(self):
            self.markers = []

        def add_marker(self, marker):
            self.markers.append(marker)

    item = Item()
    conftest.pytest_collection_modifyitems(None, [item])
    (reason,) = [m.kwargs["reason"] for m in item.markers]
    assert "not-a-secret" not in reason and "alice" not in reason
    assert "db.invalid:5984" in reason
