from xcheck import XCheck, ET



## todo: Create a normalization option so normalized values can be replaced with strings
class BoolCheck(XCheck):
    """BoolCheck(name, **kwargs)
    Checks a various number of things that could be interpreted as True.
    These check as True:
        True, true, 1, Yes, yes, T, t, Y, y
    These check as False:
        False, false, 0, No, no, N, n, F, f

    Attributes:
    none_is_false [default True] -- allows None or NoneType to be
    accepted for False.

    Returns a boolean if normalized
    """
    def __init__(self, name, **kwargs):
        self.none_is_false = kwargs.pop('none_is_false', True)
        XCheck.__init__(self, name, **kwargs)
        self._object_atts.append('none_is_false')
        self.as_string = False


    def check_content(self, item):
        ok = None

        if str(item).lower() in ['true', 'yes', '1', 't', 'y']:
            ok = True
            self.normalize_content(True)
        if str(item).lower() in ['false', 'no', '0', 'f', 'n']:
            ok = True
            self.normalize_content(False)

        if item is None or str(item).lower().strip() == 'none':
            if self.none_is_false:
                ok = True
                self.normalize_content(False)
            else:
                ok = False
                raise self.error, "BoolCheck cannot accept None"

        if ok is None:

            ok = False
            raise self.error, "Boolean checker cannot check %s" % item
        return ok


    def normalize_content(self, item):
        if str(item).lower() in ['true', 'yes', '1', 't', 'y']:
            self._normalized_value = True
        if str(item).lower() in ['false', 'no', '0', 'f', 'n']:
            self._normalized_value = False
        if self.as_string:
            self._normalized_value = str(self._normalized_value)

    def __call__(self, item, **kwargs):
        self.as_string = kwargs.pop('as_string', False)
        if self.as_string:
            kwargs['normalize'] = True
        return XCheck.__call__(self, item, **kwargs)

    def dummy_value(self):
        return 'False'

import unittest

class BoolCheckTC(unittest.TestCase):
    def setUp(self):
        self.b = BoolCheck('flag')

    def tearDown(self):
        del self.b

    def testPassWithBoolean(self):
        "BoolCheck() accepts True or False types"
        self.failUnless(self.b(True))
        self.failUnless(self.b(False))

    def testPassWithBooleanString(self):
        "BoolCheck() accepts boolean-equivalent strings"
        self.failUnless(self.b('True'))
        self.failUnless(self.b('False'))

    def testPassWithLowerCaseBoolanString(self):
        "BoolCheck() accepts boolean-equivalent strings despite capitalization"
        for x in ['true', 'TRUE', 'false', 'FALSE']:
            self.failUnless(self.b( x))

    def testPassWithYesNoAnyCase(self):
        "BoolCheck() accepts yes and no variants"
        for x in ['yes', 'YES', 'y', 'Y', 'no', 'NO', 'n', 'N']:
            self.failUnless(self.b(x))

    def testPassWithNoneAsFalse(self):
        "BoolCheck() accepts NoneType if none_is_false is True"
        self.b.none_is_false=True
        self.failUnless(self.b(None))

    def testFailWithoutNoneAnFalse(self):
        "BoolCheck() fails if NoneType and none_is_false is False"
        self.b.none_is_false = False
        self.assertRaises(self.b.error, self.b, None)

    def testPassWithNoneAsFalseAndNoneString(self):
        "BoolCheck() accepts 'None' if none_is_false is True"
        self.b.none_is_false = True
        self.failUnless(self.b('None'))

    def testFailWithoutNoneAsFalseandNoneString(self):
        "BoolCheck() fails with 'none' if none_is_false is False"
        self.b.none_is_false = False
        self.assertRaises(self.b.error, self.b, 'none')

    def testPassWithValidString(self):
        "BoolCheck() accepts a variety of positive and negative strings"
        for x in ['true','yes','1','t','y','false','no','0','f','n']:
            self.failUnless(self.b(x))
            self.failUnless(self.b(x.upper()))
            self.failUnless(self.b(x.title()))

    def testPassWithXMLText(self):
        "BoolCheck() accepts xml-formatting string"
        for x in ['true','yes','1','t','y','false','no','0','f','n']:
            self.failUnless(self.b('<flag>%s</flag>' % x))

    def testPassWithElement(self):
        "BoolCheck() accepts xml-formatting string"
        for x in ['true','yes','1','t','y','false','no','0','f','n']:
            self.failUnless(self.b(ET.fromstring('<flag>%s</flag>' % x) ) )

    def testNormalizedValues(self):
        "Boolcheck() returns the correct normalized value"
        for x in ['true','yes','1','t','y']:
            self.assertTrue(self.b(x, normalize=True))
        for x in ['false','no','0','f','n']:
            self.assertFalse(self.b(x, normalize=True))

    def test_as_string(self):
        for x in ['true','yes','1','t','y', 'TRUE', 'YES', 'Y', True]:
            self.assertEqual(self.b(x, as_string=True), 'True')
        for x in ['false','no','0','f','n','FALSE', 'F','N','NO', False]:
            self.assertEqual(self.b(x, as_string=True), 'False')

if __name__=='__main__':
    unittest.main(verbosity=1)