import sys
from urlparse import urljoin
from urllib import quote
from datetime import datetime
from hashlib import sha1

import requests
from simplejson import dumps, loads
from uuid import uuid4
import iso8601

from jsonstore.rest import OpEncoder
from jsonstore.exceptions import ConflictError


class EntryManager(object):
    def __init__(self, url, auth=None):
        if not url.endswith('/'):
            url += '/'
        self.store = url
        self.auth = auth

    def create(self, entry=None, **kwargs):
        """
        Add a new entry to the store.

        """
        if entry is None:
            entry = kwargs
        else:
            assert isinstance(entry, dict), "Entry must be instance of ``dict``!"
            entry.update(kwargs)

        # set an id, if there is none
        id_ = entry.setdefault('__id__', str(uuid4()))

        # post object
        url = urljoin(self.store, str(id_))
        r = requests.post(url, data=dumps(entry, cls=OpEncoder), auth=self.auth)
        
        if r.status_code == 409:
            raise ConflictError('Conflict, the id "%s" already exists!' % id_)
        else:
            r.raise_for_status()  # check for other errors

        entry = loads(r.content)
        entry['__updated__'] = iso8601.parse_date(entry['__updated__'])
        return entry

    def delete(self, id_):
        """
        Delete a single entry from the store.

        """
        url = urljoin(self.store, str(id_))
        r = requests.delete(url, auth=self.auth)

    def update(self, entry=None, old=None, **kwargs):
        """
        Conditionally update an entry.

        """
        if entry is None:
            entry = kwargs
        else:
            assert isinstance(entry, dict), "Entry must be instance of ``dict``!"
            entry.update(kwargs)

        id_ = entry['__id__']

        # now try to PUT it
        url = urljoin(self.store, str(id_))
        headers = {}
        if old is not None:
            headers['If-Match'] = '%s' % sha1(dumps(old, cls=OpEncoder, indent=4)).hexdigest()
        r = requests.put(url, data=dumps(entry, cls=OpEncoder), headers=headers, auth=self.auth)
        if r.status_code == 412:
            raise ConflictError("Pre-condition failed!")
        else:
            r.raise_for_status()

        entry = loads(r.content)
        entry['__updated__'] = iso8601.parse_date(entry['__updated__'])
        return entry

    def search(self, obj=None, size=None, offset=0, count=False, **kwargs):
        """
        Search database using a JSON object.

        """
        if obj is None:
            obj = kwargs
        else:
            assert isinstance(obj, dict), "Search key must be instance of ``dict``!"
            obj.update(kwargs)

        params = {}
        if size is not None:
            params['size'] = size
        if offset:
            params['offset'] = offset

        url = urljoin(self.store, quote(dumps(obj, cls=OpEncoder)))

        if count:
            r = requests.head(url, params=params)
            return int(r.headers['X-ITEMS'])
        else:
            r = requests.get(url, params=params)
            entries = r.json
            for entry in entries:
                entry['__updated__'] = iso8601.parse_date(entry['__updated__'])
            return entries

