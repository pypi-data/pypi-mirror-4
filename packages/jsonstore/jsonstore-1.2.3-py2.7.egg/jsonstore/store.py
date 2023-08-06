import sys
import os
import itertools
import operator
from datetime import datetime
import time
import re
import sqlite3
from collections import defaultdict
from threading import RLock

from uuid import uuid4
from simplejson import loads, dumps
from sqlalchemy import create_engine
import iso8601

from jsonstore.operators import Operator, Equal
from jsonstore.exceptions import ConflictError, InvalidError


# http://lists.initd.org/pipermail/pysqlite/2005-November/000253.html
def regexp(expr, item):
    p = re.compile(expr)
    return p.match(item) is not None


class EntryManager(object):
    def __init__(self, index='index.db', **kwargs):
        self.lock = defaultdict(RLock)

        if index == ':memory:':
            self.pool = create_engine('sqlite://')
        else:
            self.pool = create_engine('sqlite:///' + index)

        if index == ':memory:' or not os.path.exists(index):
            # create tables
            with self.lock[index]:
                conn = self.pool.connect()
                conn.execute("CREATE TABLE flat (id VARCHAR(255), updated timestamp, position CHAR(255), leaf NUMERIC);")
                conn.execute("CREATE INDEX position ON flat (position);")
                conn.execute("CREATE TABLE store (id VARCHAR(255), dumps NUMERIC);")
                conn.execute("CREATE INDEX id ON store (id);")
                conn.close()

    def create(self, entry=None, **kwargs):
        """
        Add a new entry to the store.

        This can be done by passing a dict, keyword arguments, or a combination of both::

            >>> from jsonstore import EntryManager
            >>> em = EntryManager('test.db')
            >>> em.create({'name': 'Roberto'}, gender='male')

        """
        if entry is None:
            entry = kwargs
        else:
            assert isinstance(entry, dict), "Entry must be instance of ``dict``!"
            entry.update(kwargs)

        id_ = entry.setdefault('__id__', str(uuid4()))
        conn = self.pool.connect()
        result = conn.execute("SELECT id FROM flat WHERE id=?", (id_,))
        if result.fetchone():
            raise ConflictError('Conflict, the id "%s" already exists!' % id_)

        # Store entry.
        with self.lock[id_]:
            self._store_entry(entry)
        return self._load_entry(id_)

    def delete(self, id_):
        """
        Delete a single entry from the store.

        Simply specify the id of the entry to be deleted::

            >>> from jsonstore import EntryManager
            >>> em = EntryManager('test.db')
            >>> em.delete(1)               # delete entry with id "1"

        The deleted entry is returned, in order to be sure that the proper 
        entry was deleted.

        """
        with self.lock[id_]:
            entry = self._load_entry(id_)
            self._delete_entry(id_)
        return entry

    def update(self, entry=None, condition=lambda old: True, **kwargs): 
        """
        Conditionally update an entry.

        This method allows an entry to be updated, as long as a condition is met. This avoids
        conflicts when two clients are trying to update an entry at the same time.

        Here's a simple example::

            >>> from jsonstore import EntryManager
            >>> em = EntryManager('test.db')
            >>> entry = em.search(__id__=1)[0]

        Suppose we have some hashing function ``hash``, we can then use it to check if the
        entry hasn't been modified before we updated it::
        
            >>> def condition(old, entry=entry):
            ...     return hash(old) == hash(entry)
            >>> entry['foo'] = 'bar' 
            >>> em.update(entry, condition)

        This is used by the REST store for conditional PUT, using etags.

        """
        if entry is None:
            entry = kwargs
        else:
            assert isinstance(entry, dict), "Entry must be instance of ``dict``!"
            entry.update(kwargs)

        id_ = entry['__id__']
        with self.lock[id_]:
            old = self._load_entry(id_)
            if not condition(old):
                raise ConflictError('Pre-condition failed!')
            self._delete_entry(id_)
            self._store_entry(entry)
            new = self._load_entry(id_)
        return new

    def search(self, obj=None, size=None, offset=0, count=False, **kwargs):
        """
        Search database using a JSON object::

            >>> from jsonstore import EntryManager
            >>> from jsonstore.operators import GreaterThan
            >>> em = EntryManager('test.db')
            >>> em.search(type='post', comments=GreaterThan(0))
        
        The algorithm works by flattening the JSON object (the "key"), and searching the
        index table for each leaf of the key using an OR. We then get those ids where the
        number of results is equal to the number of leaves in the key.
        
        """
        if obj is None:
            obj = kwargs
        else:
            assert isinstance(obj, dict), "Search key must be instance of ``dict``!"
            obj.update(kwargs)

        # Check for id.
        obj = obj.copy()
        id_ = obj.pop('__id__', None)

        # Flatten the JSON key object.
        pairs = list(flatten(obj))
        pairs.sort()
        groups = itertools.groupby(pairs, operator.itemgetter(0))

        query = ["SELECT DISTINCT id FROM flat"]
        condition = []
        params = []

        # Check groups from groupby, they should be joined within
        # using an OR.
        leaves = 0
        for (key, group) in groups:
            group = list(group)
            subquery = []
            for position, leaf in group:
                params.append(position)
                if not isinstance(leaf, Operator):
                    leaf = Equal(leaf)
                subquery.append("(position=? AND leaf %s)" % leaf)
                params.extend(leaf.params)
                leaves += 1

            condition.append(' OR '.join(subquery))

        # Build query.
        if condition or id_ is not None:
            query.append("WHERE")
        if id_ is not None:
            query.append("id=?")
            params.insert(0, id_)
            if condition:
                query.append("AND")
        if condition:
            # Join all conditions with an OR.
            query.append("(%s)" % " OR ".join(condition))
        if leaves:
            query.append("GROUP BY id HAVING COUNT(*)=%d" % leaves)
        query.append("ORDER BY updated DESC")
        if size is not None or offset:
            if size is None:
                size = sys.maxint  # we *need* a limit if offset is set
            query.append("LIMIT %s" % size)
        if offset:
            query.append("OFFSET %s" % offset)
        query = ' '.join(query)

        conn = self.pool.connect()
        if count:
            result = conn.execute(
                    "SELECT COUNT(*) FROM (%s) AS ITEMS"
                    % query, tuple(params)).fetchone()[0]
            conn.close()
            return result
        else:
            result = conn.execute(query, tuple(params)).fetchall()
            conn.close()
            return [ self._load_entry(row[0]) for row in result ]

    def _load_entry(self, id_):
        """
        Load a single entry from the store by id.

        """
        conn = self.pool.connect()
        result = conn.execute("SELECT dumps FROM store WHERE id=?", (id_,)).fetchone()
        if not result:
            raise InvalidError('No such entry: "%s"' % id_)
        result = loads(result[0])
        result['__updated__'] = iso8601.parse_date(result['__updated__'])
        conn.close()
        return result

    def _store_entry(self, entry):
        """
        Store a single entry in the store.

        """
        entry.setdefault('__updated__', datetime.utcnow())
        if isinstance(entry['__updated__'], datetime):
            entry['__updated__'] = entry['__updated__'].isoformat()

        # Index entry.
        indexes = [(entry['__id__'], entry['__updated__'], k, v)
                for (k, v) in flatten(entry) if k != '__id__']

        conn = self.pool.connect()
        conn.execute("""
            INSERT INTO flat (id, updated, position, leaf)
            VALUES (?, ?, ?, ?);
        """, indexes)
        conn.execute("""
            INSERT INTO store (id, dumps)
            VALUES (?, ?);
        """, (entry['__id__'], dumps(entry)))
        conn.close()

    def _delete_entry(self, id_):
        """
        Delete a single entry from the store by id.

        """
        conn = self.pool.connect()
        conn.execute("DELETE FROM flat WHERE id=?;", (id_,))
        conn.execute("DELETE FROM store WHERE id=?;", (id_,))
        conn.close()


def escape(name):
    try:
        return name.replace('.', '%2E')
    except TypeError:
        return name


def flatten(obj, keys=[]):
    key = '.'.join(keys)
    if isinstance(obj, list):
        for item in obj:
            for pair in flatten(item, keys):
                yield pair
    elif isinstance(obj, dict):
        for k, v in obj.items():
            for pair in flatten(v, keys + [escape(k)]):
                yield pair
    else:
        yield key, obj
