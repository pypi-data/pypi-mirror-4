import logging

from xcheck import XCheck, XCheckError
from infinity import INF, NINF

class IntCheck(XCheck):
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
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        ok = None
        try:
            data = int(item)
        except:
            ok = False
            logging.error("%s is not an integer (type %s)" % (
                item,
                type(item)))
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
            kwargs['_normalize'] = True
        return XCheck.__call__(self, item, **kwargs)

    def dummy_value(self):
        return '0' if self.min == NINF else str(self.min)

class DecimalCheck(XCheck):
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

if __name__=='__main__':
    i = IntCheck('value')
    c = DecimalCheck('cost')
    print i
    print c