import re
from urllib import unquote
from urlparse import urljoin
from datetime import datetime
from hashlib import sha1
import operator

from webob import Request, Response
from simplejson import loads, dumps, JSONEncoder

from jsonstore.store import EntryManager
from jsonstore import rison
from jsonstore import operators
from jsonstore import webhook
from jsonstore.exceptions import ConflictError, InvalidError


def make_app(global_conf, **kwargs):
    return JSONStore(**kwargs)


class OpEncoder(JSONEncoder):
    """
    A JSON encoder that converts datetime to iso.

    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, operators.Operator):
            return obj.__class__.__name__ + '(' + dumps(obj.params)[1:-1] + ')'


class JSONStore(object):
    def __init__(self, *args, **kwargs):
        """
        A REST(ish) interface to the JSON store.

        """
        self.em = EntryManager(*args, **kwargs)

    def __call__(self, environ, start_response):
        """
        Main dispatcher.

        Dispatch is done by HTTP method. It is possible to override the method using
        the ``X-HTTP-Method-Override`` header.

        """
        req = Request(environ)
        method = req.headers.get('X-HTTP-Method-Override') or req.method
        func = getattr(self, method)
        res = func(req)
        return res(environ, start_response)

    def GET(self, req):
        """
        Return a single entry or perform a search.

        The GET method can be used to retrieve a single entry from the store::

            $ curl http://localhost:8081/id
            {"foo": {"bar": ["one", "two"]}, "__id__": "id", "__updated__": ...}

        If a dict is passed, either as JSON or RISON, a search will be performed::

            $ curl 'http://localhost:8081/{"type":"test"}'
            $ curl 'http://localhost:8081/(type:test)'

        The two examples above will return elements that contain key ``type`` with value ``test``.

        """
        path_info = req.path_info.lstrip('/') or '{}'  # empty search

        # first token is either an id or a search dict
        obj = load_entry(unquote(path_info))
        if isinstance(obj, dict):
            # perform a search
            obj = replace_operators(obj)
            x_items = self.em.search(obj, count=True)
            result = self.em.search(obj, req.GET.get('size'), req.GET.get('offset'))
        else:
            # return a document
            try:
                result = self.em.search(__id__=obj)[0]
                x_items = 1
            except (IndexError, KeyError):
                return Response(status='404 Not Found')

        # encode as JSON and calculate etag from document body
        body = dumps(result, cls=OpEncoder, indent=4)
        etag = '"%s"' % sha1(body).hexdigest()
        if etag in req.if_none_match:
            return Response(status='304 Not Modified')

        # check for jsonp
        jsonp = req.GET.get('jsonp') or req.GET.get('callback')
        if jsonp:
            body = jsonp + '(' + body + ')'
            content_type = 'text/javascript'
        else:
            content_type = 'application/json'

        return Response(
                body=body,
                content_type=content_type,
                charset='utf8',
                headerlist=[('X-ITEMS', str(x_items)), ('etag', etag)])

    def HEAD(self, req):
        """
        A HEAD request. Simply do a GET and clear the body.

        """
        response = self.GET(req)
        response.body = ''
        return response

    def POST(self, req):
        """
        A POST is used to create a new document in the store.

        If no id is set in the document or in the URL, a random one is automatically
        assigned. In case an id is set *both* in the document and the URL, they need
        to be the same::

            $ curl http://localhost:8080/ -d '{}'
            {"__id__": "7da1899f-4b15-4c22-ab6a-abf7b620fa87", "__updated__": "2012-05-04T17:40:28.511880+00:00"}
            $ curl http://localhost:8080/test1 -d '{}'
            {"__id__": "test1", "__updated__": "2012-05-04T17:45:06.320792+00:00"}
            $ curl http://localhost:8080/ -d '{"__id__":"test2"}'
            {"__id__": "test2", "__updated__": "2012-05-04T17:45:50.397600+00:00"}

        """
        entry = load_entry(req.body)

        url_id = req.path_info.lstrip('/')
        if url_id:
            # if url_id is set we use it as the id, as long as it's not
            # different than entry['__id__']
            entry.setdefault('__id__', url_id)
            if str(entry['__id__']) != url_id:
                return Response(status='409 Conflict')

        try:
            result = self.em.create(entry)
        except ConflictError:
            return Response(status='409 Conflict')

        # check for webhooks
        webhook.check(self.em, entry)

        body = dumps(result, cls=OpEncoder, indent=4)
        etag = '"%s"' % sha1(body).hexdigest()
        location = urljoin(req.application_url, str(result['__id__']))

        return Response(
                status='201 Created',
                body=body,
                content_type='application/json',
                charset='utf8',
                headerlist=[('Location', location), ('etag', etag)])

    def PUT(self, req):
        """
        Update an entry with a POST.

        """
        entry = load_entry(req.body)

        url_id = req.path_info.lstrip('/')
        if '__id__' not in entry:
            entry['__id__'] = url_id
        elif url_id != str(entry['__id__']):
            return Response(status='409 Conflict')

        # Conditional PUT. This is useful for implementing counters, eg.
        def condition(old):
            etag = '%s' % sha1(dumps(old, cls=OpEncoder, indent=4)).hexdigest()  # no quotes to check against req.if_match
            return etag in req.if_match or (
                    req.if_unmodified_since and 
                    req.if_unmodified_since >= old['__updated__'])
        try:
            result = self.em.update(entry, condition)
        except InvalidError:
            return Response(status='404 Not Found')
        except ConflictError:
            return Response(status='412 Precondition Failed')

        # check for webhooks
        webhook.check(self.em, entry)

        body = dumps(result, cls=OpEncoder, indent=4)
        etag = '"%s"' % sha1(body).hexdigest()

        return Response(
                body=body,
                content_type='application/json',
                charset='utf8',
                headerlist=[('etag', etag)])

    def PATCH(self, req):
        """
        PATCH an entry, replacing only part of the document.

        We simple load the full entry, apply the patch and PUT it.

        """
        patch = load_entry(req.body)
        id_ = req.path_info.lstrip('/')

        if '__id__' in patch and patch['__id__'] != id_:
            return Response(status='409 Conflict')

        old = self.em.search(__id__=id_)[0]
        new = old.copy()

        def replace(entry, patch):
            for k, v in patch.items():
                if isinstance(v, dict):
                    replace(entry[k], v)
                else:
                    entry[k] = v
        replace(new, patch)
        req.body = dumps(new, cls=OpEncoder)
        return self.PUT(req)

    def DELETE(self, req):
        """
        DELETE a single entry.

        """
        id_ = req.path_info.lstrip('/')
        entry = self.em.delete(id_)

        # check for webhooks
        webhook.check(self.em, entry)

        return Response(
                status='204 No Content',
                body='',
                content_type='application/json',
                charset='utf8')


def load_entry(s):
    """
    Try to load user input as JSON, then RISON, then as string.

    """
    try:
        entry = loads(s)
    except ValueError:
        try:
            entry = rison.loads(s)
        except (ValueError, rison.ParserException):
            entry = s
    return entry


def replace_operators(obj):
    """
    Operators like ``GreaterThan`` need to be encoded as a string
    on the JSON/RISON object. If we find a string which matches an
    operator we evaluate it.

    """
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = replace_operators(v)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                obj[k][i] = parse_op(item)
        else:
            obj[k] = parse_op(v)
    return obj


def parse_op(obj):
    """
    Parse and evaluate a string that matches a know operator.

    """
    if not isinstance(obj, basestring):
        return obj

    for op in operators.__all__:
        m = re.match(op + r'\((.*?)\)', obj)
        if m:
            operator = getattr(operators, op)
            args = m.group(1)
            args = loads('[' + args + ']')
            return operator(*args)
    return obj


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = JSONStore('index.db')
    run_simple('127.0.0.1', 31415, app)
