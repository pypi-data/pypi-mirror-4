import re

from core import XCheck
from infinity import INF

#todo: Add no_spaces_allowed option (default False)
class TextCheck(XCheck):
    """TextCheck(name[, min_length, max_length, pattern])
    TextCheck validates text or elements with string values

    :param min_length: Minimum length of text (default 0)
    :type min_length: integer
    :param max_length: Maximum length of text (default INF)
    :type max_length: integer or INF
    :param pattern: regex that can be used to check the text (default None)

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
    """EmailCheck(name [allow_none, allow_blank])
    Creates a checker specializing in email addresses


    :param allow_none: allows NoneType or case-insensitive 'none' instead of an email address
    :type allow_none: boolean (default True)
    :param allow_blank: allows an empty or blank string instead of an email address
    :type allow_blank: boolean (default False)
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
    """UrlCheck(name [, allow_none, allow_blank])
    Creates a checker specializing in URLs

    :param allow_none: allows NoneType or case-insensitive 'none' instead of a URL
    :type allow_none: boolean (default True)
    :param allow_blank: allows an empty or blank string instead of a URL
    :type allow_blank: boolean (default False)

    This checker uses the urlparse module from the Python distribution.
    """
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

import unittest
from core import ET

class TextCheckTC(unittest.TestCase):
    def setUp(self):
        self.t = TextCheck('text', min_length = 4, max_length = 8)

    def tearDown(self):
        del self.t

    def testDefaults(self):
        "TextCheck creates the proper default attributes"
        t = TextCheck('text')
        self.assertEqual(t.min_length, 0, "min_length not 1")
        self.assertEqual(t.max_length, INF, "max_length not 1")
        self.assertEqual(t.pattern, None, "pattern not None")

    def testCustomizedAttributes(self):
        "TextCheck customizes attributes"
        t = TextCheck('text', min_length=4, max_length=8, pattern=r'blah')
        self.assertEqual(t.min_length, 4, "min_length not set correctly")
        self.assertEqual(t.max_length, 8, "max_length not set correctly")
        self.assertEqual(t.pattern, r'blah', "pattern not set correctly")

    def testPassWithMinString(self):
        "TextCheck() accepts strings of the minimum length"
        self.failUnless(self.t('abcd') )

    def testPassWithMaxString(self):
        "TextCheck() accepts strings of the maximum length"
        self.failUnless(self.t('abcdefgh'), \
            "TextCheck() accepted a string longer than the maximum length")

    def testPassWithElement(self):
        "TextCheck() accepts an elementtree.Element"
        self.failUnless(self.t(ET.fromstring('<text>abcde</text>') ) )

    def testPassWithElementString(self):
        "TextCheck() accepts an xml-formatted string"
        self.failUnless(self.t('<text>abcdef</text>'))

    def testFailWithTooShortString(self):
        "TextCheck() fails if the string is too short"
        self.assertRaises(self.t.error, self.t, "abc")

    def testFailWithTooLongString(self):
        "TextCheck() fails if the string is too long"
        self.assertRaises(self.t.error, self.t, "123456789")

    def testFailWithTooShortElement(self):
        "TextCheck() fails if the element.text is too short"
        self.assertRaises(self.t.error, self.t,
            ET.fromstring('<text>abc</text>') )

    def testFailWithTooShortXMLString(self):
        "TextCheck() fails if the xml string text is too short"
        self.assertRaises(self.t.error, self.t, '<text>a</text>')

    def testFailWithEmptyElement(self):
        "TextCheck() fails if the xml element has no text but checker expects some"
        self.assertRaises(self.t.error, self.t, '<text />')

    def testPassWithEmptyElement(self):
        "TextCheck() passes if the xml element is empty and the checker's min_length is 0"
        t = TextCheck('note', min_length=0)
        t('<note />')

    def testPassWithPattern(self):
        "TextCheck() accepts strings that match the given pattern"
        t = TextCheck('test', pattern=r'\S+@\S+\.\S+')
        self.failUnless(t('english@spiritone.com') )

    def testFailWithPattern(self):
        "TextCheck() fails if the string doesn't match the given pattern"
        t = TextCheck('test', pattern=r'\S+@\S+\.\S+')
        self.assertRaises(t.error, t, 'english @ spiritone.com')

    def testNormalization(self):
        self.assertEqual(self.t('Joshua', normalize=True), "Joshua",
            "TextCheck not normalizing properly")

    def testNormalizingNone(self):
        self.assertRaises(self.t.error, self.t, None, normalize=True)

class EmailCheckTC(unittest.TestCase):
    def setUp(self):
        self.t = EmailCheck('email')
        self.n = EmailCheck('email', allow_none = False)
        self.b = EmailCheck('email', allow_blank = True)

    def tearDown(self):
        del self.t
        del self.n
        del self.b

    def testDefaultEmail(self):
        "EmailCheck() accepts valid simple email addresses"
        self.failUnless(self.t('english@example.com'))

    def testDefaults(self):
        "EmailCheck creates the proper default attributes"
        self.assertTrue(self.t.allow_none, "allow_none not True")
        self.assertFalse(self.t.allow_blank, "allow_blank not False")

    def testDefaultEmailasNoneString(self):
        "EmailCheck() defaults to allow 'None'"
        self.failUnless(self.t('None'))

    def testDefaultEmailAsNone(self):
        "EmailCheck() defaults to allow None object"
        self.failUnless(self.t(None))

    def testDefaultEmailAsBlank(self):
        "EmailCheck() fails if email is blank and allow_blank is False"
        self.assertRaises(self.t.error, self.t, '')

    def testCustomAllowNone(self):
        "EmailCheck handles allow_none=False"
        self.failIf(self.n.allow_none)

    def testFailCustomAllowNone(self):
        "EmailCheck() fails if allow_none is false and given None"
        self.assertRaises(self.n.error, self.n, 'None')

    def testFailCustomAllowBlank(self):
        "EmailCheck() allows a blank string if allow_blank is true"
        self.failUnless(self.b(''))

    def testFailCustomAllowBlankEmpty(self):
        "EmailCheck() allows an empty string if allow_blank is true"
        self.failUnless(self.b(' '))

if __name__=='__main__':
##    logger = logging.getLogger()
##    logger.setLevel(logging.CRITICAL)

    unittest.main(verbosity=1)
