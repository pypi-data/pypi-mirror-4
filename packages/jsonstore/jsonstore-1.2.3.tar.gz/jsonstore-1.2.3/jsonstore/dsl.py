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
    def __init__(self, uri, auth=None):
        """
        Instatiate a local or remote JSONStore.

        """
        if uri.startswith('http'):
            self.em = client.EntryManager(uri, auth)
        else:
            self.em = store.EntryManager(uri)

    def __repr__(self):
        """
        Display contents.

        """
        return repr(self.em.search())

    def __rrshift__(self, entry):
        """
        Create or update a new entry.

        """
        if '__id__' in entry:
            results = self.em.search(__id__=entry['__id__'])
            if results:
                return self.em.update(entry, results[0])
        return self.em.create(entry)

    def __rlshift__(self, entry):
        """
        Delete an entry.

        """
        return self.em.delete(entry['__id__'])

    def __div__(self, token):
        """
        Return a document.

        """
        return self.em.search(__id__=token)[0]

    def __or__(self, token):
        """
        Return a search.

        """
        return self.em.search(token)

    def __len__(self):
        return self.em.search(count=True)

    def __iter__(self):
        return iter(self.em.search())

    def __contains__(self, entry):
        return bool(self.em.search(__id__=entry['__id__'], count=True))
