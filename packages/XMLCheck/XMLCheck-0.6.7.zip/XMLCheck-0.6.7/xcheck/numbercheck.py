import logging

from core import XCheck, XCheckError
from infinity import INF, NINF


class IntCheck(XCheck):
    """IntCheck(name[, min, max])

    IntCheck checks attributes and elements containing integer data.

    :param name: name of the xml tag
    :type name: string
    :param min: minimum value for the checker
    :type min: integer or NINF
    :param max: maximum value for the checker
    :type max: integer or INF

    The max and min attributes are inclusive, they default to NINF and INF,
    respectively.
    """
    def __init__(self, name, **kwargs):
        self.min = NINF
        self.max = INF
        self.error = XCheckError
        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['min', 'max'])
        self.as_string = False

    def normalize_content(self, item):
        self._normalized_value = int(item)
        if self.as_string:
            self._normalized_value = str(self._normalized_value)

    def check_content(self, item):
        logging.debug("check_content(%s) type %s" % (item, type(item)))
        ok = None
        try:
            if isinstance(item, basestring):
                item = float(item)
            data = int(item)
        except:
            ok = False
            raise ValueError("item not an integer")

        if float(item) != int(item):
            ok = False
            raise TypeError("cannot convert float")

        if ok is not None:
            return ok

        ok = True

        ok = self.min <= data <= self.max
        if not ok:
            raise self.error("item out of bounds")
        self.normalize_content(item)
        return ok

    def __call__(self, item, **kwargs):
        self.as_string = kwargs.pop('as_string', False)
        if self.as_string:
            kwargs['normalize'] = True
        return XCheck.__call__(self, item, **kwargs)

    def dummy_value(self):
        return '0' if self.min == NINF else str(self.min)

class DecimalCheck(XCheck):
    """DecimalCheck(name[, min, max])

    DicimalCheck checks attributes and elements containing float data.

    :param name: name of the xml tag
    :type name: string
    :param min: minimum value for the checker
    :type min: integer or NINF
    :param max: maximum value for the checker
    :type max: integer or INF

    The max and min attributes are inclusive, they default to NINF and INF,
    respectively.
    """

    def __init__(self, name, **kwargs):
        self.min = NINF
        self.max = INF
        self.error = XCheckError
        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['min', 'max'])

    def normalize_content(self, item):
        self._normalized_value = float(item)

    def check_content(self, item):
        ok = None

        try:
            data = float(item)
        except:
            ok = False
            raise ValueError, "'%s' not a float value" % item

        if ok is not None:
            return ok

        ok = True
        ok &= (self.min <= data )
        if not ok:
            raise self.error, "%f too low" % data
        ok &= (data <= self.max)
        if not ok:
            raise self.error, "%f too high" % data
        self.normalize_content(data)
        return ok

    def dummy_value(self):
        return '0' if self.min == NINF else str(self.min)


import unittest
from core import ET

class IntCheckTC(unittest.TestCase):
    "These test if the defaults are created properly"
    def setUp(self):
        self.t = IntCheck('test', min=1, max = 10)
    def tearDown(self):
        del self.t

    #~ valid input tests
    def test_pass_with_integer(self):
        "IntCheck() accepts in-bounds integer"
        self.failUnless(self.t( 9))

    def test_pass_with_valid_string(self):
        "IntCheck() accepts integer-equivalent string"
        self.failUnless(self.t( '6'))

    def test_pass_with_valid_float(self):
        "IntCheck() accepts with integer-equivalent float"
        self.failUnless(self.t( 6.0 ) )

    def test_pass_with_valid_float_string(self):
        "IntCheck() accepts strings of integer-equivalent floats"
        self.failUnless(self.t('6.0'))

    def test_pass_with_element(self):
        "IntCheck() accepts valid element.text"
        self.failUnless(self.t(ET.fromstring('<test>4</test>')))

    def test_pass_with_xml(self):
        "IntCheck() accepts valid xml strings"
        self.failUnless(self.t('<test>4</test>'))

    #~ bad input tests
    def test_fail_with_empty_string(self):
        "IntCheck() raises ValueError when passed an empty string when required"
        self.assertRaises(ValueError, self.t, '')

    def test_fail_with_oob_int(self):
        "IntCheck() fails with out-of-bounds integer"
        self.assertRaises(self.t.error, self.t, -4)

    def test_fail_with_float(self):
        "IntCheck() raises TypeError when passed with non-integral float"
        self.assertRaises(TypeError, self.t, 5.6)

    def test_fail_with_oob_string(self):
        "IntCheck() fails with out-of-bounds integral string"
        self.assertRaises(self.t.error, self.t, '45')

    def test_fail_with_float_string(self):
        "IntCheck() fails when passed float-equivalent string"
        self.assertRaises(TypeError, self.t, '5.6')

    def test_fail_with_float_elem(self):
        "IntCheck() raises ValueError with element.text as non-integral float"
        self.assertRaises(TypeError, self.t, ET.fromstring('<test>5.5</test>') )

    def test_fail_with_float_elem_string(self):
        "IntCheck() fails with xml-formatting string as non integral float"
        self.assertRaises(TypeError, self.t, '<test>5.4</test>')

    def test_fail_with_oob_element(self):
        "IntCheck() fails with element.text as out-of-bounds integer"
        self.assertRaises(self.t.error, self.t, ET.fromstring('<test>99</test>'))

    def test_fail_with_oob_element_string(self):
        "IntCheck() fails with xml-formattet sting with out of bounds integer"
        self.assertRaises(self.t.error, self.t, '<test>99</test>')

    def test_fail_with_non_integer(self):
        "IntCheck() fails with a non-integer"
        self.assertRaises(ValueError, self.t, 'a')

    def test_normalization(self):
        self.assertEqual(self.t('9', normalize=True), 9,
            "IntCheck normalized bunged a string")
        self.assertEqual(self.t(9, normalize=True), 9,
            "IntCheck normalize bunged an integer")

    def test_bugfix004(self):
        self.assertEqual(self.t(9, as_string=True), '9')

class DecimalCheckTC(unittest.TestCase):
    "These test if the defaults are created properly"
    def setUp(self):
        self.t = DecimalCheck('test', min=1, max = 10)
    def tearDown(self):
        del self.t

    def test_pass_with_float(self):
        "DecimalCheck() accepts in-bounds floats values"
        self.failUnless(self.t(5.0))

    def test_pass_with_integer(self):
        "DecimalCheck() accepts in-bounds integer values"
        self.failUnless(self.t(5))

    def test_pass_with_float_string(self):
        "DecimalCheck() accepts in-bounds strings representing floats"
        self.failUnless(self.t('4.3'))

    def test_pass_with_integer_string(self):
        "DecimalCHeck() accepts in-bounds strings representing integers"
        self.failUnless(self.t('5'))

    def test_pass_with_element(self):
        self.failUnless(self.t(ET.fromstring('<test>4.5</test>')))

    def test_pass_with_element_string(self):
        self.assertTrue(self.t('<test>4.5</test>'))

    # Bad Input tests
    def test_fail_with_empty_string(self):
        self.assertRaises(ValueError, self.t, '')

    def test_fail_with_oob_float(self):
        self.assertRaises(self.t.error, self.t, 0.5)
        self.assertRaises(self.t.error, self.t, 12.4)

    def test_fail_with_oob_string(self):
        self.assertRaises(self.t.error, self.t, '0.5')
        self.assertRaises(self.t.error, self.t, '12.4')

    def test_fail_with_crap_value(self):
        self.assertRaises(ValueError, self.t, 'fail')


if __name__=='__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)

    unittest.main(verbosity=1)