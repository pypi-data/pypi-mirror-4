
Redis Collections
=================

Set of basic Python collections backed by Redis.

Status: ACTIVE
--------------

Under active development and maintenance.

Example
-------

Redis Collections are a simple, pythonic way how to access Redis structures::

    >>> from redis_collections import Dict
    >>> d = Dict()
    >>> d['answer'] = 42
    >>> d
    <redis_collections.Dict fe267c1dde5d4f648e7bac836a0168fe>
    >>> d.items()
    [('answer', 42)]
    >>> d.update({'hasek': 39, 'jagr': 68})
    >>> dict(d.items())
    {'answer': 42, 'jagr': 68, 'hasek': 39}
    >>> del d['answer']
    >>> dict(d.items())
    {'jagr': 68, 'hasek': 39}

Available collections are ``Dict``, ``List``, ``Set``.

Documentation
-------------

**→** `redis-collections.readthedocs.org <https://redis-collections.readthedocs.org/>`_

License: ISC
------------

© 2013 Jan Javorek <jan.javorek@gmail.com>

This work is licensed under `ISC license <https://en.wikipedia.org/wiki/ISC_license>`_.
