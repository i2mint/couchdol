# couchdol

couchdb with a simple (dict-like or list-like) interface

The server URL defaults to the `COUCHDB_URL` environment variable when it is
set, else `http://127.0.0.1:5984` (see [`default_couchdb_url()`](#couchdol.default_couchdb_url)).

### Module Attributes

| [`COUCHDB_URL_ENVVAR`](#couchdol.COUCHDB_URL_ENVVAR)   | Environment variable naming the default CouchDB server URL.   |
|-----------------------------------------------------------------------|---------------------------------------------------------------|
| [`DFLT_COUCHDB_URL`](#couchdol.DFLT_COUCHDB_URL)     | URL used when `COUCHDB_URL` is not set.                       |

### Functions

| [`default_couchdb_url`](#couchdol.default_couchdb_url)()   | The CouchDB URL stores use when none is given: `$COUCHDB_URL` or the local default.   |
|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------|

### Classes

| [`CouchDbPersister`](#couchdol.CouchDbPersister)([user, password, url, ...])      | A basic couchDB persister.     |
|----------------------------------------------------------------------------------------------------|--------------------------------|
| [`CouchDbStore`](#couchdol.CouchDbStore)([user, password, url, db_name, ...]) |                                |
| [`CouchDbTupleKeyStore`](#couchdol.CouchDbTupleKeyStore)([user, password, url, ...])  | CouchDbStore using tuple keys. |

### couchdol.COUCHDB_URL_ENVVAR *= 'COUCHDB_URL'*

Environment variable naming the default CouchDB server URL.

### *class* couchdol.CouchDbPersister(user='admin', password='admin', url=None, db_name='py2store', key_fields=('_id',), couchdb_client_kwargs=None)

Bases: `KvPersister`

A basic couchDB persister.
Note that the couchDB persister is designed not to overwrite the value of a key if the key already exists.
You can subclass it and use update_one instead of insert_one if you want to be able to overwrite data.

```pycon
>>> s = CouchDbPersister()
>>> for _id in s:  # deleting all docs in tmp
...     del s[_id]
>>> k = {'_id': 'foo'}
>>> v = {'val': 'bar'}
>>> k in s  # see that key is not in store (and testing __contains__)
False
>>> len(s)
0
>>> s[k] = v
>>> len(s)
1
>>> list(s)
[{'_id': 'foo'}]
>>> s[k]
{'val': 'bar'}
>>> s.get(k)
{'val': 'bar'}
>>> s.get({'not': 'a key'}, {'default': 'val'})  # testing s.get with default
{'default': 'val'}
>>> list(s.values())
[{'val': 'bar'}]
>>> k in s  # testing __contains__ again
True
>>> del s[k]
>>> len(s)
0
>>>
>>> s = CouchDbPersister(db_name='py2store', key_fields=('name',), data_fields=('yob', 'proj', 'bdfl'))
>>> for _id in s:  # deleting all docs in tmp
...     del s[_id]
>>> s[{'name': 'guido'}] = {'yob': 1956, 'proj': 'python', 'bdfl': False}
>>> s[{'name': 'vitalik'}] = {'yob': 1994, 'proj': 'ethereum', 'bdfl': True}
>>> for key, val in s.items():
...     print(f"{key}: {val}")
{'name': 'guido'}: {'yob': 1956, 'proj': 'python', 'bdfl': False}
{'name': 'vitalik'}: {'yob': 1994, 'proj': 'ethereum', 'bdfl': True}
```

#### clear()

The clear method is disabled to make dangerous difficult.
You don’t want to delete your whole DB
If you really want to delete all your data, you can do so by doing something like this:

```python
for k in self:
    del self[k]
```

or (in some cases)

```python
for k in self:
    try:
        del self[k]
    except KeyError:
        pass
```

### *class* couchdol.CouchDbStore(user='admin', password='admin', url=None, db_name='py2store', key_fields=('_id',), couchdb_client_kwargs=None)

Bases: `Store`

#### clear()

The clear method is disabled to make dangerous difficult.
You don’t want to delete your whole DB
If you really want to delete all your data, you can do so by doing something like this:

```python
for k in self:
    del self[k]
```

or (in some cases)

```python
for k in self:
    try:
        del self[k]
    except KeyError:
        pass
```

### *class* couchdol.CouchDbTupleKeyStore(user='admin', password='admin', url=None, db_name='py2store', key_fields=('_id',), couchdb_client_kwargs=None)

Bases: [`CouchDbStore`](#couchdol.CouchDbStore)

CouchDbStore using tuple keys.

```pycon
>>> s = CouchDbTupleKeyStore(key_fields=('_id', 'user'))
>>> k = (1234, 'user')
>>> v = {'name': 'bob', 'age': 42}
>>> if k in s:  # deleting all docs in tmp
...     del s[k]
>>> assert (k in s) == False  # see that key is not in store (and testing __contains__)
>>> orig_length = len(s)
>>> s[k] = v
>>> assert len(s) == orig_length + 1
>>> assert k in list(s)
>>> assert s[k] == v
>>> assert s.get(k) == v
>>> assert v in list(s.values())
>>> assert (k in s) == True # testing __contains__ again
>>> del s[k]
>>> assert len(s) == orig_length
```

### couchdol.DFLT_COUCHDB_URL *= 'http://127.0.0.1:5984'*

URL used when `COUCHDB_URL` is not set.

### couchdol.default_couchdb_url()

The CouchDB URL stores use when none is given: `$COUCHDB_URL` or the local default.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
