from couchdol import CouchDbStore, CouchDbTupleKeyStore


def test_couchdb_store(couchdb_url, s=None, k=None, v=None):
    # Instantiate lazily: a default-arg store would connect at collection time.
    if s is None:
        s = CouchDbStore(url=couchdb_url)
    if k is None:
        k = {"_id": "foo"}
    if v is None:
        v = {"val": "bar"}
    if k in s:  # deleting all docs in tmp
        del s[k]
    assert (
                   k in s
           ) is False  # see that key is not in store (and testing __contains__)
    orig_length = len(s)
    s[k] = v
    assert len(s) == orig_length + 1
    assert k in list(s)
    assert s[k] == v
    assert s.get(k) == v
    assert v in list(s.values())
    assert (k in s) is True  # testing __contains__ again
    del s[k]
    assert len(s) == 0

    # tuple as key test
    s = CouchDbTupleKeyStore(url=couchdb_url, key_fields=("_id", "user"))
    k = (1234, "user")
    v = {"name": "bob", "age": 42}
    if k in s:  # deleting all docs in tmp
        del s[k]
    assert (
                   k in s
           ) is False  # see that key is not in store (and testing __contains__)
    orig_length = len(s)
    s[k] = v
    assert len(s) == orig_length + 1
    assert k in list(s)
    assert s[k] == v
    assert s.get(k) == v
    assert v in list(s.values())
    assert (k in s) is True  # testing __contains__ again
    del s[k]
    assert len(s) == orig_length


def test_default_url_follows_couchdb_url_envvar(monkeypatch):
    # the probe, the tests and default-constructed stores must agree on the server
    from couchdol import DFLT_COUCHDB_URL, default_couchdb_url

    monkeypatch.setenv("COUCHDB_URL", "http://couch.example:1234")
    assert default_couchdb_url() == "http://couch.example:1234"
    monkeypatch.delenv("COUCHDB_URL")
    assert default_couchdb_url() == DFLT_COUCHDB_URL
