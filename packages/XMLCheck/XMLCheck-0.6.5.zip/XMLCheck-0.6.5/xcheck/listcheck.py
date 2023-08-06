import operator

from xcheck import XCheckError, XCheck
from boolcheck import BoolCheck
from infinity import INF, NINF

class NoSelectionError(XCheckError):
    """SelectionCheck was not given a value to check"""
class BadSelectionsError(XCheckError):
    """SelectionCheck was passed non-iterable as whitelist"""

class SelectionCheck(XCheck):
    """SelectionCheck(name, **kwargs)
    SelectionCheck checks against a set number of string values
    values -- a required list of string objects
    ignore_case [default True] -- allows value to match upper or lower case
    """
    _boolCheck = BoolCheck('caseSensitive')
    def __init__(self, name, **kwargs):
        try:
            self.values = list(kwargs.pop('values', []))
        except:
            raise BadSelectionsError("Selection must be iterable")

        self.values = [val for val in self.values if val]

        self.ignore_case = self._boolCheck(kwargs.pop('ignore_case', True),
            normalize=True)

        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['ignore_case', 'values'])

        if not self.values:
            raise NoSelectionError("must have values for selection test")
        for v in self.values:
            if not isinstance(v, basestring):
                raise BadSelectionsError("value %s is not string type" % v)

    def check_content(self, item):
        ok = None
        item = str(item)
        vals = list(self.values)
        self.normalize_content(item)
        if self.ignore_case:
            item = item.lower()
            vals = map(str.lower, vals)
        if item not in vals:
            ok = False
            raise self.error(
                "Selection %s not in list of available values" % item)
        else:
            ok = True
        return ok

    def dummy_value(self):
        return self.values[0]

strip = operator.methodcaller('strip')
lower = operator.methodcaller('lower')
upper = operator.methodcaller('upper')
title = operator.methodcaller('title')

class ListCheck(XCheck):
    """ListCheck(name, **kwargs)
    List Check accepts a string that is formatted as a list

    Attributes:
    delimiter [default ','] -- The separator between items
    values [default []] -- The acceptable values for each item
        if values exists, each item in the list will be checked that it
        exists in the list, otherwise, anything can be a member of the list
    allow_duplicates [default False] -- if True, items can appear more than once
        in the list. If false, items can only appear once
    min_items [default 0] -- the minimum number of items allowed in the list
    max_items [default INF] -- the maximum number if items allowed in the list
    ignore_case [default False] -- if True, check is not case-sensitive

    In the call:
    _normalize = True returns a python list [default]
    as_string -- returns a string representation

    """
    _boolCheck = BoolCheck('ignore_case')
    def __init__(self, name, **kwargs):
        self.delimiter = kwargs.pop('delimiter', ',')
        self.values = kwargs.pop('values', [])
        self.allow_duplicates = kwargs.pop('allow_duplicates', False)
        self.min_items = int(kwargs.pop('min_items', 0) )
        self.max_items = int(kwargs.pop('max_items', -1) )
        self.ignore_case = self._boolCheck(
            kwargs.pop('ignore_case', False),
            normalize=True)

        if self.max_items in [ -1, INF]:
            self.max_items = INF

        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['delimiter', 'values', 'allow_duplicates',
            'min_items', 'max_items', 'ignore_case'])

    def normalize_content(self, items):
        "normalizes the content of the list"
        self._normalized_value = map(strip, items)
        if self.as_string:
            delim = "%s " % self.delimiter
            self._normalized_value = delim.join(self._normalized_value)



    def check_content(self, item):
        "determines if items in list are valid"
        ok = True
        if item is None:
            item = ''
        if isinstance(item, (list, tuple)):
            item = self.delimiter.join(item)
        items = item.split(self.delimiter)
        items = map(strip, items)
        items = filter(bool, items)
        if self.min_items > len(items):
            ok = False
            raise self.error, "not enough items in the list"
        if self.max_items < len(items):
            ok = False
            raise self.error, "too many items in the list"
        if self.ignore_case:
            vals = map(str.lower, self.values)
            items = map(str.lower, items)
        else:
            vals = list(self.values)

        if vals != []:
            for item in items:
                ok &= item in vals
                if item not in vals:
                    raise self.error, "Item %s not in values list(%s)" % \
                        (item, self.name)
                if not self.allow_duplicates:
                    try:
                        vals.remove(item)
                    except ValueError:
                        raise self.error, "Item %s not in values list" % item

        if not ok:
            raise self.error, "sommat got borked"
        self.normalize_content(items)
        return ok

    def __call__(self, item, **kwargs):
        self.as_string = kwargs.pop('as_string', False)
        if self.as_string:
            kwargs['normalize'] = True
        return XCheck.__call__(self, item, **kwargs)

    def dummy_value(self):
        if self.values:
            return self.delimiter.join(self.values[:self.min_items])
        else:
            from string import lowercase
            return self.delimiter.join(lowercase[:self.min_items])


if __name__=='__main__':
    s = SelectionCheck('thing', values=['one', 'two', 'five'])
    print s
    l = ListCheck('other')
    print l
