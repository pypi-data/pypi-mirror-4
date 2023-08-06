"""
This is a simple DSL for working with JSONStore.

Suppose we're running a JSONStore server:

    $ jsonstore
     * Running on http://127.0.0.1:31415/

We can interact with it like this:

    >>> from jsonstore.dsl import Store
    >>> from jsonstore.operators import *
    >>> store = Store("http://localhost:31415/")
    >>> print store
    []

Let's add something to our store:

    >>> entry = { "__id__": 1, "type": "pet", "name": "Minhoca", "age": 4 }
    >>> entry >> store
    {'age': 4, 'type': 'pet', '__id__': 1, '__updated__': <...>, 'name': 'Minhoca'}
    >>> entry in store
    True

And one more:

    >>> { "type": "person", "name": "Roberto", "age": 34, "interests": ["Python", "JSON"] } >> store
    {'interests': ['Python', 'JSON'], 'name': 'Roberto', 'age': 34, '__updated__': <...>, '__id__': <...>, 'type': 'person'}

Let's list our documents:

    >>> for doc in store:
    ...     print doc['name']
    Roberto
    Minhoca

Now for some fun:

    >>> print store/1
    {u'age': 4, u'type': u'pet', u'__id__': 1, u'__updated__': <...>, u'name': u'Minhoca'}

    >>> print store | { "type": "person" }
    [{u'interests': [u'Python', u'JSON'], u'name': u'Roberto', u'age': 34, u'__updated__': <...>, u'__id__': <...>, u'type': u'person'}]

Remove some elements:

    >>> for doc in store | dict(age=LessThan(30)):
    ...     doc << store
    ...
    >>> print entry in store
    False
    >>> print store
    [{u'interests': [u'Python', u'JSON'], u'name': u'Roberto', u'age': 34, u'__updated__': <...>, u'__id__': <...>', u'type': u'person'}]

"""

from jsonstore import client, store


class Store(object):
    """
    A JSONStore that can be manipulated using a Pythonic DSL.

    """
    def __init__(self, em, *args, **kwargs):
        """
        Instantiate a local or remote JSONStore.

        """
        if isinstance(em, (client.EntryManager, store.EntryManager)):
            self.em = em
        elif em.startswith('http'):
            self.em = client.EntryManager(em, *args, **kwargs)
        else:
            self.em = store.EntryManager(em)

    def __repr__(self):
        """
        Display contents.

        """
        return repr(self.em.search())

    def __rrshift__(self, other):
        """
        Create or update a new entry.

            doc = { "a": 1 }
            entry = doc >> store

        """
        if '__id__' in other:
            results = self.em.search(__id__=other['__id__'])
            if results:
                return self.em.update(other, old=results[0])
        return self.em.create(other)

    def __rlshift__(self, other):
        """
        Delete an entry, or a list of entries.

            >>> entry << store

        """
        if isinstance(other, dict):
            self.em.delete(other['__id__'])

    def __div__(self, other):
        """
        Return a document.

            >>> id = 'foo'
            >>> entry = store/id

        """
        return self.em.search(__id__=other)[0]

    def __or__(self, other):
        """
        Return a search.

            >>> for entry in store | { "type": "post" }:
            ...     print entry

        We can pass this to another Store:

            >>> store1 | store2

        """
        if isinstance(other, dict):
            return self.em.search(other)
        elif isinstance(other, Store):
            for entry in self.em.search():
                entry >> other 

    def __ror__(self, other):
        """
        Add elements to a store.

           >>> store1 | { "type": "post" } | store2 

        """
        for entry in other:
            entry >> self

    def __len__(self):
        return self.em.search(count=True)

    def __iter__(self):
        return iter(self.em.search())

    def __contains__(self, entry):
        return bool(self.em.search(__id__=entry['__id__'], count=True))
