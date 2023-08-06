import datetime

from xcheck import XCheck
from utils import get_bool

class DatetimeCheck(XCheck):
    """DateTimeCheck(name, **kwargs)
    Checks date and time formatted strings, date objects, and time objects.
    Attributes:
    allow_none [default False] -- allows NoneType or equivalent string
    format [default "%a %b %d %H:%M:%S %Y"] -- the format to use while checking
    formats or formatList [default an empty list] -- several string formats
    minDateTime [default datetime.datetime.min (year is 1900)] -- minimum date
    maxDateTime [default datetime.date.max] -- maximum date

    Additional attributes in __call__
    as_datetime [default False] -- normalizes the value to a
        datetime.datetime object
    as_struct [default False] -- normalizes the value to a
        time.struct_time object
    as_string [default True] -- normalzes the value to a string formatted
        according to the format argument or the first format in the
        formats list.

    DateTimeCheck ignores custom use of _normalize. If any of as_datetime,
        as_struct, or as_string are true, _normalize will be set to True.
    """

    def __init__(self, name, **kwargs):
        self.allow_none = get_bool(kwargs.pop('ignore_case', False))
        self.format = kwargs.pop('format', "%a %b %d %H:%M:%S %Y")
        self.formats = kwargs.pop('formats', [])
        self.min_datetime = kwargs.pop('minDateTime',
            datetime.datetime.min.replace(year=1900))
        self.max_datetime = kwargs.pop('maxDateTime', datetime.datetime.max)
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
            raise self.error, "Date out of bounds"

        return ok

    def __call__(self, item, **kwargs):
        self.as_datetime = kwargs.pop('as_datetime', False)
        self.as_struct = kwargs.pop('as_struct', False)
        self.as_string = kwargs.pop('as_string', True)

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
        raise ValueError, "cannot normalize %s" % item

    def dummy_value(self):
        if self.allow_none:
            return 'None'
        else:
            return self.normalize_content(self.min_datetime)

if __name__=='__main__':
    d = DateTimeCheck('sent')
    print d