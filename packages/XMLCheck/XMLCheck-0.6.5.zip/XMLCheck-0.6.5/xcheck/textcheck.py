import re

from xcheck import XCheck
from infinity import INF

#todo: Add no_spaces_allowed option (default False)
class TextCheck(XCheck):
    """TextCheck(name, **kwargs)
    TextCheck validates text or elements with string values

    Attributes:
    min_length [default 0] -- the minimum length of the text
    max_length [default INF] -- the maximum length allowed
    pattern [default None] -- a regular expression that can
        be used to check the data.
    """
    def __init__(self, name, **kwargs):
        self.min_length = 0
        self.max_length = INF
        self.pattern = None
        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['min_length', 'max_length', 'pattern'])

    def check_content(self, item):
        ok = isinstance(item, basestring)
        if item is None:
            if self.min_length > 0:
                raise self.error("Expected some text")
            else:
                return True
        if  len(item) < self.min_length:
            ok = False
            raise self.error("Text too short")
        if len(item) > self.max_length:
            ok = False
            raise self.error("Text too long")
        if self.pattern is not None:
            if not bool(re.search( self.pattern, item) ):
                ok = False
                raise self.error("Text failed to match pattern")

        if item is None:
            raise self.error('Generic text error')
        self.normalize_content(item)

        return ok

    def dummy_value(self):
        start = ord('A')
        res = []
        for x in range(self.min_length):
            res.append(chr(start) )
            start += 1
        return ''.join(res)


class EmailCheck(TextCheck):
    """EmailCheck(name, **kwargs)
    Creates a checker specializing in email addresses

    Attributes:
    allow_none [default True] -- allows NoneType or case-insensitive 'none'
        instead of an email address
    allow_blank [default False] -- allows an empty or blank string instead of
        an email address
    """
    _emailMatch = re.compile(r'\S+@\S+\.\S+')

    def __init__(self, name, **kwargs):
        self.allow_none = kwargs.pop('allow_none', True)
        self.allow_blank = kwargs.pop('allow_blank', False)

        TextCheck.__init__(self, name, **kwargs)
        self.pattern = r'\S+@\S\.\S'
        self._object_atts.extend(['allow_none', 'allow_blank'])

    def check_content(self, item):
        ok = None
        if item in [None, 'None', 'none']:
            if self.allow_none:
                ok = True
                self.normalize_content('None')
            else:
                raise self.error("None not allowed as email")
                ok = False

        if ok is None:
            if not item.strip():
                if self.allow_blank:
                    ok = True
                    self.normalize_content('')
                else:
                    ok = False
                    raise self.error("Blank email not allowed")

        if ok is None:
            if  self._emailMatch.match( item) :
                ok = True
            else:
                ok = False
                raise self.error(
                    "%sCheck failed to match %s" % (self.name, item))
        if ok:
            self.normalize_content(item)

        return ok

    def normalize_content(self, item):
        self._normalized_value = str(item)

    def dummy_value(self):
        return "me@example.com"

class URLCheck(TextCheck):
    def __init__(self, name, **kwargs):
        self.allow_none = kwargs.pop('allow_none', True)
        self.allow_blank = kwargs.pop('allow_blank', False)

        TextCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['allow_none', 'allow_blank'])


    def check_content(self, item):
        ok = None
        if item in [None, 'None', 'none']:
            if self.allow_none:
                ok = True
                self.normalize_content('None')
            else:
                raise self.error, "None not allowed as url"
        if ok is None:
            if not item.strip():
                if self.allow_blank:
                    ok = True
                    self.normalize_content('')
                else:
                    ok = False
                    raise self.error, "Blank url not allowed"
        if ok is None:
            from urlparse import urlparse
            parsed_url = urlparse(item)
            if parsed_url.netloc:
                ok = True
            else:
                ok = False
                raise self.error(
                    "%sCheck failed to match %s" % (self.name, item) )
        if ok:
            self.normalize_content(item)
        return ok

    def normalize_content(self, item):
        self._normalized_value = str(item)

    def dummy_value(self):
        return "http://www.example.com"


