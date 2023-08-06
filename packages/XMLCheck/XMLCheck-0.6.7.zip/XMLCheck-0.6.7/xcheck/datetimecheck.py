import datetime

from core import XCheck
from utils import get_bool

class DatetimeCheck(XCheck):
    """DateTimeCheck(name[, keywords])
    Checks date and time formatted strings, date objects, and time objects.

    :param allow_none: allows NoneType or equivalent string to be treated as False
    :type allow_none: Boolean (default False)
    :param format: the format to use while checking (see Python documentation)
    :type format: str (default "%a %b %d %H:%M:%S %Y")
    :param formats: several string formats for alternate use
    :type formats: list of strings
    :param formatlist: alias for formats
    :param min_datetime: minimum date
    :type min_datetime: datetime.date (default Jan. 1, 1900)
    :param max_datetime: maximum date
    :type max_datetime: datetime.date (default datetime.date.max)

    Additional attributes in __call__

    :param as_datetime: normalizes the value to a datetime.datetime object
    :param as_struct: normalizes the value to atime.struct_time object
    :param as_string: normalzes the value to a string

    DateTimeCheck ignores custom use of _normalize. If any of as_datetime,
        as_struct, or as_string are true, _normalize will be set to True.

    By defaulet `as_string` is `True` and `as_datetime` and
    `as_struct` are False in the call.
    """

    def __init__(self, name, **kwargs):
        self.allow_none = get_bool(kwargs.pop('ignore_case', False))
        self.format = kwargs.pop('format', "%a %b %d %H:%M:%S %Y")
        self.formats = kwargs.pop('formats', [])
        self.min_datetime = kwargs.pop('min_datetime',
            datetime.datetime.min.replace(year=1900))
        self.max_datetime = kwargs.pop('max_datetime', datetime.datetime.max)
        #print self.min_datetime
        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['allow_none', 'format', 'formats',
            'min_datetime', 'max_datetime'])


        if not isinstance(self.min_datetime, datetime.datetime):
            try:
                self.min_datetime = datetime.datetime.strptime(
                    self.min_datetime, self.format)
            except:
                raise self.error("cannot parse minimum date")

        if not isinstance(self.max_datetime, datetime.datetime):
            try:
                self.max_datetime = datetime.datetime.strptime(
                    self.max_datetime, self.format)
            except:
                raise self.error("cannot parse maximum date")

        self.as_datetime =  False
        self.as_struct = False
        self.as_string =  True

    def check_content(self, item):
        ok = False
        parsed_date = None
        is_none = False

        if self.format:
            try:
                parsed_date = datetime.datetime.strptime(str(item), self.format)
                self._normalized_value = self.normalize_content(parsed_date)
                ok = True
            except Exception:
                pass # if this fails, will try a different method

        if not ok:
            for fmt in self.formats:
                try:
                    parsed_date = datetime.datetime.strptime(str(item), fmt)
                    self._normalized_value = self.normalize_content(parsed_date)
                    ok = True
                    break
                except:
                    pass

        if self.allow_none and str(item).lower() == 'none':
            ok = True
            self._normalized_value = "None"
            is_none = True

        if ok is False:
            raise self.error, "Cannot parse %s as date" % item

        if not is_none and not (
                self.min_datetime <= parsed_date <= self.max_datetime):
            raise self.error("Date out of bounds")

        return ok

    def __call__(self, item, **kwargs):
        self.as_datetime = kwargs.pop('as_datetime', False)
        self.as_struct = kwargs.pop('as_struct', False)
        self.as_string = kwargs.pop('as_string', False)

        kwargs['normalize'] = any(
            [self.as_datetime, self.as_struct, self.as_string])

        return XCheck.__call__(self, item, **kwargs)

    def normalize_content(self, item):
        #print 'normalizing', item
        if self.as_datetime:
            return item #~ should already be a date time object
        elif self.as_struct:
            return item.timetuple() #~ should
        else:
            if self.format:
                return item.strftime(self.format)
            else:
                return item.strftime(self.formats[0])
        raise ValueError("cannot normalize %s" % item)

    def dummy_value(self):
        if self.allow_none:
            return 'None'
        else:
            return self.normalize_content(self.min_datetime)

import unittest
import time

class DatetimeCheckTC(unittest.TestCase):
    def setUp(self):
        self.d = DatetimeCheck('date')

    def tearDown(self):
        del self.d

    def test_defaults(self):
        "DatetimeCheck creates appropriate default values"
        self.assertFalse(self.d.allow_none, "allow_none not False")
        self.assertEqual(self.d.format, "%a %b %d %H:%M:%S %Y",
            "format not the default")
        self.assertEqual(self.d.formats, [], "formats not an empty list")

    def test_custom_attributes(self):
        "DatetimeCheck customizes attrbutes"
        d = DatetimeCheck('date', allow_none=True, format="%b-%d-%Y",
            formats = ['%d-%m-%Y',])
        self.assertTrue(d.allow_none, "allow_none not customized")
        self.assertEqual(d.format, '%b-%d-%Y', 'format not customised')
        self.assertEqual(d.formats, ['%d-%m-%Y'])

    def test_default_format(self):
        "DatetimeCheck() accepts the default Datetime"
        self.failUnless(self.d('Mon Oct 26 22:20:43 2009'),
            "cannot parse default date")

    def test_custom_format(self):
        "DatetimeCheck() accepts a custom format"
        d = DatetimeCheck('test', format="%Y%m%d%H%M%S")
        self.failUnless(d('20090101122042'), 'cannot parse custom date')

    def test_datetime_object(self):
        "DatetimeCheck() returns a Datetime.Datetime object when requested"
        dt = self.d("Mon Oct 26 14:52:42 2009", as_datetime=True)
        self.assertIsInstance(dt, datetime.datetime,
            "Did not return a datetime.datetime object")

    def test_as_struct(self):
        "DatetimeCheck() returns a time.struct_time object when requested"
        dt = self.d("Mon Oct 26 09:00:00 2009", as_struct=True)
        self.assertIsInstance(dt, time.struct_time,
            "Did not return a time.struct_time object")

    def test_as_string(self):
        "DatetimeCheck() returns a string by when requested"
        dt = self.d("Sat Jul 14 11:00:00 2001", as_string=True)
        self.assertTrue(isinstance(dt, basestring),
            "Did not return a string by default")

    def test_boolean_result(self):
        "DatetimeCheck() return a boolean if all as_xxx options are False"
        dt = self.d("Sat Jul 14 11:00:00 2001", as_string = False)
        self.assertTrue(isinstance(dt, bool), "Did not return a boolean")

    def test_date_out_of_bounds(self):
        "DatetimeCheck() fails if date is out of range"
        d = DatetimeCheck('test', format="%m/%d/%Y",
            min_datetime = "10/1/2009",
            max_datetime = "10/31/2009")
        self.assertRaises(self.d.error, d, "9/30/2009")

    def test_month_and_day_only(self):
        "DatetimeCheck() accepts month and day only"
        d = DatetimeCheck('mday', format="%b %d", min_datetime="Oct 10",
            max_datetime="Oct 20")
        self.failUnless(d('Oct 12'), "Cannot accept month and day only")
        self.assertRaises(d.error, d, 'Oct 9')
        self.assertRaises(d.error, d, 'Nov 1')

    def test_format_lists(self):
        "DatetimeCheck() handles a list of formats"
        d = DatetimeCheck('formatlist', formats=['%b %d', '%b %d %Y'])
        self.failUnless(d('Oct 1'),
            "DatetimeCheck() cannot handle the first format")
        self.failUnless(d('Jan 1 2000'),
            "DatetimeCheck() cannot handle the second format")

    def test_allow_none(self):
        "DatetimeCheck() allows None, optionally"
        d = DatetimeCheck('date', allow_none = True)
        self.failUnless(d('None'), "Fails to accept string None")
        self.failUnless(d(None), "Fails to accept None type")
        self.failUnless(d('<date>None</date>'), "Fails to accept string-node")
        self.failUnless(d('<date>none</date>'),
            "DatetimeCheck() fails to accept 'none' as node text")
        self.failUnless(d('none'), "Fails to accept 'none' as text")

if __name__=='__main__':
##    logger = logging.getLogger()
##    logger.setLevel(logging.CRITICAL)

    unittest.main(verbosity=1)