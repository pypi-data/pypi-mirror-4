from core import XCheck, XCheckError
from textcheck import TextCheck, EmailCheck, URLCheck
from boolcheck import BoolCheck
from listcheck import NoSelectionError, BadSelectionsError
from listcheck import SelectionCheck, ListCheck
from numbercheck import IntCheck, DecimalCheck
from datetimecheck import DatetimeCheck
from utils import get_elem
from infinity import INF, NINF
import logging

LOAD_RULES = {'xcheck': XCheck,
    'selection':SelectionCheck,
    'text': TextCheck,
    'int': IntCheck,
    'datetime': DatetimeCheck,
    'decimal': DecimalCheck,
    'list': ListCheck,
    'url': URLCheck,
    'email': EmailCheck,
    'bool': BoolCheck
}

class XCheckLoadError(XCheckError): pass
class UnmatchedError(XCheckError): pass

INT_ATTRIBUTES = ['min_length', 'max_length', 'min_occurs',
            'max_occurs', ]

BOOL_ATTRIBUTES = ['required', 'unique', 'check_children', 'ordered',
    'allow_none', 'allow_blank', 'none_is_false']

STR_OR_NONE_ATTRIBUTES = ['pattern']

def num_or_inf(val, func):
    if val in [INF, 'Infinity', 'INF', 'InfinityPlus']:
        return INF
    elif val in [NINF, 'NINF', 'InfinityMinus']:
        return NINF
    else:
        return func(val)

def load_checker(node):
    "takes an elementtree.element node and recreates the checker"
    node = get_elem(node)
    if node.tag not in LOAD_RULES:
        raise XCheckLoadError, "Cannot create checker for %s" % node.tag

    new_atts = {}

    # Selection definition node uses delimiter, but selection check doesn't
    delimiter = node.get('delimiter', ',')

    for key in node.keys():
        if key == 'delimiter':
            if node.tag == 'list':
                val = delimiter


        val = node.get(key)

        if key=='values':
            val = map(str.strip, val.split(delimiter))

        if key in INT_ATTRIBUTES:
            val = num_or_inf(val, int)

        if key in BOOL_ATTRIBUTES:
            val = get_bool(val)

        if key in STR_OR_NONE_ATTRIBUTES:
            if val.lower() == 'none':
                val = None

        if key in ['min', 'max', 'min_value', 'max_value']:
            if node.tag == 'int':
                val = num_or_inf(val, int)
            elif node.tag == 'decimal':
                val = num_or_inf(val, float)

        if key in ['error']:
            if val in globals():
                val = globals()[val]
            else:
                val = UnmatchedError
        new_atts[key] = val

    ch = LOAD_RULES[node.tag](**new_atts)


    attributes = node.find('attributes')
    if attributes is not None:
        for att in attributes:
            ch.addattribute(load_checker(att))

    children = node.find('children')
    if children is not None:
        for child in children:
            ch.add_child(load_checker(child))
    return ch

import unittest
from utils import get_bool
import datetime
class OopsError(XCheckError): pass

class LoaderTC(unittest.TestCase):

    def test_xcheck_defaults(self):
        ch = load_checker('<xcheck name="person" />')
        self.assertTrue(isinstance(ch, XCheck))
        self.assertEqual(ch.name, 'person', "load_checker() did not set name")
        self.assertEqual(ch.min_occurs, 1, "load_checker() did not set min_occurs default")
        self.assertEqual(ch.max_occurs, 1, "load_checker() did not set max_occurs default")
        self.assertEqual(ch.children, [], "load_checkr() did not create empty children default")
        self.assertFalse(ch.unique, "load_checker() did not create default unique attribute")
        self.assertTrue(ch.required, "load_checker() did not create default required attribute ")
        self.assertEqual(ch.error, XCheckError, "load_checker() did not cerate default Error")
        self.assertTrue(ch.check_children)
        self.assertTrue(ch.ordered)
        self.assertEqual(ch.helpstr, '')


    def test_xcheck_customized(self):
        ch = load_checker('<xcheck name="dude" min_occurs="2" max_occurs="5" unique="true" required="false" check_children="false" helpstr="text" ordered="false" />')
        self.assertEqual(ch.name, 'dude')
        self.assertEqual(ch.min_occurs, 2, "load_checker() did not create custom min_occurs")
        self.assertEqual(ch.max_occurs, 5, "load_checker() did not creat custom max_occurs")
        self.assertTrue(ch.unique, "load_checker() did not create custom unique")
        self.assertFalse(ch.required, "load_checer() did not create custom required")
        self.assertFalse(ch.check_children)
        self.assertEqual(ch.help, 'text', "load_checker() did not create custom help")
        self.assertFalse(ch.ordered, "load_checker() did not customize ordered attribute")

    def test_text_check(self):
        ch = load_checker('<text name="title" />')
        self.assertEqual(ch.name, 'title')

        self.assertEqual(ch.min_length, 0)
        self.assertEqual(ch.max_length, INF)
        self.assertIsNone(ch.pattern)

        self.assertIsInstance(ch, TextCheck)

    def test_text_custom(self):
        ch = load_checker('<text name="id" pattern="\d{0,5}" />')

        self.assertEqual(ch.pattern, '\d{0,5}', "load_checker() did not customize pattern")
        self.assertTrue(ch("13"))

    def test_email_default(self):
        ch = load_checker('<email name="work" />')
        self.assertTrue(ch.allow_none)
        self.assertFalse(ch.allow_blank)
        self.assertTrue(ch('test@example.com'))
        self.assertIsInstance(ch, EmailCheck)

    def test_email_custom(self):
        ch =load_checker('<email name="work" allow_none="False" allow_blank="True" />')
        self.assertFalse(ch.allow_none)
        self.assertTrue(ch.allow_blank)

    def test_url_default(self):
        ch = load_checker('<url name="work" />')
        self.assertTrue(ch.allow_none)
        self.assertFalse(ch.allow_blank)
        self.assertTrue(ch('http://www.example.com'))
        self.assertIsInstance(ch, URLCheck)

    def test_url_custom(self):
        ch =load_checker('<url name="work" allow_none="False" allow_blank="True" />')
        self.assertFalse(ch.allow_none)
        self.assertTrue(ch.allow_blank)

    def test_bool(self):
        ch = load_checker('<bool name="active" />')
        self.assertTrue(ch.none_is_false)
        self.assertTrue(ch('yes'))
        self.assertIsInstance(ch, BoolCheck)

    def test_bool_custom(self):
        ch = load_checker('<bool name="active" none_is_false="False" />')
        self.assertFalse(ch.none_is_false)

    def test_selection(self):
        ch = load_checker('<selection name="type" values="home, work, cell" />')
        self.assertEqual(ch.values, ['home','work','cell'])
        self.assertTrue(ch.ignore_case)
        self.assertIsInstance(ch, SelectionCheck)

    def test_selection_partition(self):
        ch = load_checker('<selection name="range" values="a,z|0,9" delimiter="|" />')
        self.assertEqual(ch.values, ['a,z', '0,9'])

    def test_selection_custom(self):
        ch = load_checker('<selection name="test" values="1,2,3" ignore_case="false" />')
        self.assertFalse(ch.ignore_case)

    def test_selection_failure(self):
        self.assertRaises(NoSelectionError,load_checker,'<selection name="fail" />')
        self.assertRaises(NoSelectionError,load_checker,'<selection name="fail" values="" />')

    def test_int(self):
        ch = load_checker('<int name="value" />')
        self.assertEqual(ch.min, NINF)
        self.assertEqual(ch.max, INF)
        self.assertIsInstance(ch, IntCheck)

    def test_int_custom(self):
        ch = load_checker('<int name="value" min="3" max="10" />')
        self.assertEqual(ch.min, 3)
        self.assertEqual(ch.max, 10)

    def test_decimal(self):
        ch = load_checker('<decimal name="amps" />')
        self.assertEqual(ch.min, NINF)
        self.assertEqual(ch.max, INF)
        self.assertIsInstance(ch, DecimalCheck)

    def test_decimal_custom(self):
        ch = load_checker('<decimal name="test" min="-1.4" max="1.5" />')
        self.assertEqual(ch.min, -1.4)
        self.assertEqual(ch.max, 1.5)


    def test_list(self):
        ch = load_checker('<list name="items" />')
        self.assertEqual(ch.delimiter, ',')
        self.assertEqual(ch.values, [])
        self.assertFalse(ch.allow_duplicates)
        self.assertEqual(ch.min_items, 0)
        self.assertEqual(ch.max_items, INF)
        self.assertFalse(ch.ignore_case)
        self.assertIsInstance(ch, ListCheck)

    def test_list_with_items(self):
        ch = load_checker('<list name="items" values="one, two" />')
        self.assertEqual(ch.values, ['one','two'])

    def test_list_customs(self):
        ch =load_checker('<list name="items" values="one+two" delimiter="+" min_items="4" max_items="10" allow_duplicates="true" ignore_case="true"/>')

        self.assertEqual(ch.values, ['one','two'])
        self.assertEqual(ch.delimiter, "+")
        self.assertEqual(ch.min_items, 4)
        self.assertEqual(ch.max_items, 10)
        self.assertTrue(ch.allow_duplicates)
        self.assertTrue(ch.ignore_case)

    def test_datetime(self):
        ch = load_checker('<datetime name="sent" />')
        self.assertFalse(ch.allow_none)
        self.assertEqual(ch.format ,'%a %b %d %H:%M:%S %Y')
        self.assertEqual(ch.formats, [])
        self.assertEqual(ch.min_datetime,datetime.datetime(1900,1,1))
        self.assertEqual(ch.max_datetime,datetime.datetime.max)
        self.assertIsInstance(ch, DatetimeCheck)

    def test_attributes(self):
        text= """<xcheck name="person">
        <attributes>
            <int name="id" min="1"/>
        </attributes>
        <children>
            <xcheck name="name">
            <children>
                <text name="first" />
                <text name="last" />
            </children>
            </xcheck>
        </children>
        </xcheck>
        """
        ch = load_checker(text)
        self.assertEqual(ch.name, 'person')
        self.assertIn('id', ch.attributes)
        self.assertIsInstance(ch.get('id'), IntCheck)

        self.assertTrue(ch('<person id="4"><name><first>Josh</first><last>English</last></name></person>'))

##    def test_dude(self):
##        dude_def = dude.to_definition_node()
####        indent(dude_def)
####        ET.dump(dude_def)
##        new_ch = load_checker(dude_def)
##        new_ch(dudeNode)

    def test_load_errors(self):
        ch = load_checker("<text name='oops' error='TypeError' />")
        self.assertTrue(issubclass(ch.error, XCheckError))

    def test_uknown_error(self):
        "load_checker() substitutes UnmatchedError if custom error doesn't exist"
        ch = load_checker("<text name='oops' error='googoogoojoob' />")
        self.assertTrue(issubclass(ch.error, UnmatchedError))

    def test_custom_error(self):
        "load_checker() assigns custom error class"

        ch = load_checker("<text name='oops' error='OopsError' />")
        self.assertTrue(issubclass(ch.error, OopsError), "load_checker did not load OopsError")
        self.assertTrue(issubclass(ch.error, XCheckError), "load_checker did not load subclass of XCheckError")


if __name__=='__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)

    unittest.main(verbosity=1)
