from xcheck import XCheck

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