import requests
try:
    from requests import async
except RuntimeError:
    async = False
    import threading


def check(em, entry):
    """
    Check if there are any webhooks related to the entry, and call them.

    Right now we simply perform a GET if there is any webhook monitoring the
    entry. It may be interesting to delete the hook if the server is not 
    responding after a number of tries.

    """
    urls = []
    for webhook in em.search(type='__webhook__'):
        if ('pattern' in webhook and 'url' in webhook and
                match(webhook['pattern'], entry)):
            urls.append(webhook['url'])

    if async:
        rs = [async.get(url) for url in urls]
        responses = async.map(rs)
    else:
        for url in urls:
            threading.Thread(target=requests.get, args=(url,)).start()


def match(pattern, entry):
    """
    Check if a JSON pattern is inside a given entry.

    Special care must be considered when using lists. In this case, the
    elements in the pattern must be present in the entry, although it 
    doesn't have to contain all elements::

        >>> match({"var": {}}, {"var": {"baz": [1,2,3]}})
        True
        >>> match({"var": {"baz": 3}}, {"var": {"baz": [1,2,3]}})
        True 
        >>> match({"var": {"baz": [1, 3]}}, {"var": {"baz": [1,2,3]}})
        True 

    This works with operators too::

        >>> from jsonstore.operators import *
        >>> match({'foo': In(1,2,3)}, {'foo': 1})
        True
        >>> match({'foo': In(1,2,3)}, {'foo': 10})
        False

    """
    # dispatch every element of the pattern
    if isinstance(pattern, dict):
        for k, v in pattern.items():
            if isinstance(v, dict):
                if not match(v, entry.get(k, {})):
                    return False
            else:
                if not match(v, entry.get(k)):
                    return False
        return True
    
    # here we do the comparisons
    # first, if pattern is a list
    elif isinstance(pattern, list):
        # entry must be a list
        if not isinstance(entry, list):
            return False
        # all elements in pattern must be in entry
        for item in pattern:
            if item not in entry:
                return False
        return True
    
    # if entry is a list, but pattern is not, a single
    # element must match
    elif isinstance(entry, list):
        for item in entry:
            if match(pattern, item):
                return True
        return False
    
    # else do a direct comparison
    else:
        return pattern == entry
