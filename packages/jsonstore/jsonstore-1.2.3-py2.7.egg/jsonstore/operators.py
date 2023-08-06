import operator
import re

__all__ = ['Operator', 'Equal', 'NotEqual', 'GreaterThan', 'LessThan',
           'GreaterEqual', 'LessEqual', 'Between', 'In', 'Like',
           'RegExp', 'Exists']


class Operator(object):
    pass


class Comparison(Operator):
    """
    A base class for comparisons.

    """

    func = None
    op = None

    def __init__(self, value):
        self.value = value
        self.params = [value]

    def __eq__(self, item):
        return self.func(item, self.value)

    def __str__(self):
        return "%s ?" % self.op


class Equal(Comparison):
    func = operator.eq
    op = '='


class NotEqual(Comparison):
    func = operator.ne
    op = '!='


class GreaterThan(Comparison):
    func = operator.gt
    op = '>'


class LessThan(Comparison):
    func = operator.lt
    op = '<'


class GreaterEqual(Comparison):
    func = operator.ge
    op = '>='


class LessEqual(Comparison):
    func = operator.le
    op = '<='


class Between(Operator):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.params = self.start, self.end

    def __eq__(self, item):
        return self.start <= item < self.end

    def __str__(self):
        return "BETWEEN ? AND ?"


class In(Operator):
    def __init__(self, *args):
        self.params = args

    def __eq__(self, item):
        return item in self.params

    def __str__(self):
        return "IN (%s)" % ','.join('?' for arg in self.params)


class Like(Operator):
    def __init__(self, value):
        self.params = [value]
        # Naive conversion from LIKE syntax to REGEXP; does not account
        # for escaped ``%`` and ``_``.
        pattern = re.escape(value).replace(r'\%', '.*').replace(r'\_', '.')
        self.regexp = re.compile(pattern)

    def __eq__(self, item):
        return self.regexp.match(item) is not None

    def __str__(self):
        return "LIKE ?"
    

class RegExp(Operator):
    def __init__(self, value):
        self.params = [value]
        self.regexp = re.compile(value)

    def __eq__(self, item):
        return self.regexp.match(item) is not None

    def __str__(self):
        return "REGEXP ?"


class Exists(Operator):
    def __init__(self):
        self.params = []

    def __eq__(self, item):
        return item is not None

    def __str__(self):
        return "NOTNULL"
