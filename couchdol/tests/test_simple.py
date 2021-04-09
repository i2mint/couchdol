from couchdol import CouchDbStore


def test_couchdb_store(s=CouchDbStore(), k=None, v=None):
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
    s = CouchDbTupleKeyStore(key_fields=("_id", "user"))
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
