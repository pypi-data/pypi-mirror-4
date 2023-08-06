#~ -----------------------------------------
#~ UNIT TESTS
#~ -----------------------------------------
import unittest

try:
    from elementtree import ElementTree as ET
except:
    import xml.etree.ElementTree as ET

import datetime
import time

from  xcheck import *


### This can be used by several different tests
##dude = XCheck('dude', help="A simple contact list item")
nick = BoolCheck('nick', required=False)
fname = TextCheck('first', min_length = 1)
fname.addattribute(nick)

lname = TextCheck('last', min_length = 1)
code = IntCheck('code', min_occurs = 1, max_occurs = 5)
code.addattribute(TextCheck('word', required=False) )
name = XCheck('name', children=[fname, lname, code])

emailtype = SelectionCheck('type', values = ['home','work', 'personal'])
email = EmailCheck('email', max_occurs=2)
email.addattribute(emailtype)
street = TextCheck('street')
city = TextCheck('city')

address = XCheck('address', children = [street, city, email], max_occurs = 4)

dude = XCheck('dude', children=[name, address],
    help="A simple contact list item")
idch = IntCheck('id', required=True)
dude.addattribute(idch)

dudeText = """<dude id="1">
        <name>
            <first nick="true">Josh</first>
            <last>English</last>
            <code>12</code>
            <code word="answer">42</code>
        </name>
        <address>
            <street>100 Main St</street>
            <city>Podunk</city>
            <email type="home">dude@example.com</email>
            <email type="work">dude@slavewage.com</email>
        </address>
        <address>
            <street>318 West Nowhere Ln</street>
            <city>East Podunk</city>
            <email type="personal">dude@home.net</email>
        </address>
        </dude>"""

dudeNode = ET.fromstring(dudeText)


class XCheckTC(unittest.TestCase):
    def setUp(self):
        self.c = XCheck('test')

    def tearDown(self):
        del self.c

    def testBadXMLTag(self):
        self.assertRaises(self.c.error, self.c, '<text/>')

    ### testfailNormalization doesn't work as expected.
##    def testfailNormalization(self):
##         "XCheck() fails if _normalize is True but no normalizedValue is created"
##         self.assertRaises(self.c.error, self.c, '<test/>', _normalize=True)

    def testDefaults(self):
        "XCheck sets the proper default attributes on creation"
        self.assertEqual(self.c.min_occurs, 1, "min_occurs is not 1")
        self.assertEqual(self.c.max_occurs, 1, "max_occurs is not 1")
        self.assertEqual(self.c.children, [], "children not an empty list")
        self.assertEqual(self.c.unique, False, "unique not False")
        self.assertEqual(self.c.required, True, "required not True")
        self.assertEqual(self.c.attributes, {},
            "attributes not an empty dictionary")
        self.assertTrue(issubclass(self.c.error, Exception),
            "error not derived from Exception")
        self.assertTrue(self.c.check_children, "check_children not True")
        self.assertTrue(self.c.ordered, "ordered not True")

    def testCustomizationOfAttributes(self):
        "XCheck customizes attributes on creation"
        children = [XCheck('a'), XCheck('b')]
        attributes = {'c': XCheck('c')}
        c = XCheck('test', min_occurs=2, max_occurs = 3, children= children,
            unique = True, required=False, attributes = attributes,
            error=TypeError,
            check_children = False, ordered=False)
        self.assertEqual(c.name, 'test', "name is incorrect")
        self.assertEqual(c.min_occurs, 2, "min_occurs not set correctly")
        self.assertEqual(c.max_occurs, 3, "max_occurs not set correctly")
        self.assertEqual(c.children, children, "children not set correctly")
        self.assertTrue(c.unique, "unique not set correctly")
        self.assertFalse(c.required, "required not set correctly")
        self.assertEqual(c.attributes, attributes,
            "attributes not set correctly")
        self.assertEqual(c.error, TypeError, "error not set correctly")
        self.assertFalse(c.check_children, "check_children not set correctly")
        self.assertFalse(c.ordered, "ordered not set correctly")

    def testGetChild(self):
        "XCheck.get() returns appropriate checkers"
        attcheck = BoolCheck('attribute', required=True)
        childcheck = TextCheck('child')
        childcheck.addattribute(attcheck)
        check = XCheck('check', children = [childcheck])

        self.assertEqual(check.get('child'), childcheck)
        self.assertEqual(check.get('attribute'), attcheck)

        ach = check.get('attribute')
        self.assertEqual(ach.name, 'attribute')

class AttributesTC(unittest.TestCase):
    def setUp(self):
        self.val = IntCheck('val', min=1, max=10, error=TypeError)
        self.t = XCheck('test')
        self.t.addattribute(self.val)

    def tearDown(self):
        del self.t
        del self.val

    def testFailWithBadAttribute(self):
        "XCheck raises XMLAttributeError on adding non-XCheck attribute"
        for item in ['a', 2, 4.5, TypeError]:
            self.assertRaises(XMLAttributeError, self.t.addattribute, item)

    def testFailWithBadAttributeDictionary(self):
        "XCheck raises XMLAttributeError if attribute dictionary is ill-formed"
        self.assertRaises(XMLAttributeError, XCheck, 'name',
            attributes={'this': XCheck('that')} )

    def testFailWithNonXCheckAttributeDictionary(self):
        "XCheck raises XMLAttributeError if attributes dictionary values are not XCheck objects"
        self.assertRaises(XMLAttributeError, XCheck, 'name',
        attributes={'this':'that'} )

    def testPassWithGoodAttribute(self):
        "XCheck.addattribute() adds valid attributes"
        self.t.addattribute(XCheck('b') )
        self.failUnless('b' in self.t.attributes,
            'did not append attribute properly')

    def testAttributeValidation(self):
        "XCheck() accepts valid attribute values"
        self.failUnless(self.t('<test val="3" />'))

    def testNonRequiredAttribute(self):
        "XCheck() accepts a missing non-required attribute"
        self.t.attributes['val'].required = False
        self.failUnless(self.t('<test />'))

    def testDoubleAttribute(self):
        "XCheck.addattribute() raises XMLAttributeError trying to add a second attribute with duplicate name"
        self.assertRaises(XMLAttributeError, self.t.addattribute, TextCheck('val'))

    def testBadAttribute(self):
        "XCheck() fails if an attribute doesn't check"
        self.assertRaises(self.val.error, self.t, '<test val="0" />')

    def testExtraAttribute(self):
        "XCheck() raises UnknownXMLAttributeError if element attribute is unknown"
        self.assertRaises(UnknownXMLAttributeError, self.t,
            '<test val="4" ex="true"/>')

    def testUnchecked(self):
        "XCheck() raises UncheckedXMLAttributeError if a required attribute was not checked"
        self.assertRaises(UncheckedXMLAttributeError, self.t, '<test />')

    def testEmptyAttribute(self):
        "XCheck() raises ValueError if value for required attribute is empty"
        self.assertRaises(ValueError, self.t, '<test val=""/>')

class UnorderedChildrenTC(unittest.TestCase):
    def setUp(self):
        self.c = XCheck('test', ordered=False)
        self.c.add_child(XCheck('a') )
        self.c.add_child(XCheck('b', min_occurs = 0, max_occurs = 2) )
        self.c.add_child(XCheck('c') )

    def tearDown(self):
        del self.c

    def testAcceptableVariations(self):
        "Unordered check accepts children in order"
        self.failUnless(self.c('<test><a/><b/><c/></test>'),
            "Unordered check didn't like ABC")
        self.failUnless(self.c('<test><a/><c/><b/></test>'),
            "Unordered check didn't like ACB")
        self.failUnless(self.c('<test><b/><a/><c/></test>'),
            "Unordered check didn't like BAC")
        self.failUnless(self.c('<test><b/><c/><a/></test>'),
            "Unordered check didn't like BCA")
        self.failUnless(self.c('<test><c/><a/><b/></test>'),
            "Unordered check didn't like CAB")
        self.failUnless(self.c('<test><c/><b/><a/></test>'),
            "Unordered check didn't like CBA")
        self.failUnless(self.c('<test><a/><c/></test>'),
            "Unordered check didn't like AC")
        self.failUnless(self.c('<test><c/><a/></test>'),
            "Unordered check didn't like CA")
        self.failUnless(self.c('<test><a/><b/><b/><c/></test>'),
            "Unordered check didn't like ABBC")
        self.failUnless(self.c('<test><b/><a/><b/><c/></test>'),
            "Unordered check didn't like BABC")
        self.failUnless(self.c('<test><b/><b/><a/><c/></test>'),
            "Unordered check didn't like BBAC")

    def testUnexpectedChild(self):
        "Unordered check fails if it finds an unexpected child"
        self.assertRaises(UnexpectedChildError, self.c,
            '<test><unwanted/></test>')

    def testNotEnoughChidren(self):
        "Unordered check fails if it doesn't find enough children"
        self.assertRaises(MissingChildError, self.c,
            '<test><b/><b/><c/></test>')
        self.assertRaises(MissingChildError, self.c, '<test><a/></test>')

    def testTooManyChildren(self):
        "Unordered check fails if it finds too many children"
        self.assertRaises(UnexpectedChildError, self.c,
            '<test><a/><a/><c/></test>')
        self.assertRaises(UnexpectedChildError, self.c,
            '<test><a/><b/><b/><b/><c/></test>')
        self.assertRaises(UnexpectedChildError, self.c,
            '<test><a/><b/><c/><c/></test>')


class ChildrenTC(unittest.TestCase):
    def setUp(self):
        self.p = XCheck('parent')
        c = XCheck('child')
        self.p.add_child(c)
        self.m = XCheck('kid', min_occurs=2, max_occurs= 3)

    def tearDown(self):
        del self.p
        del self.m

    def testPassChildren(self):
        "XCheck() accepts known children elements"
        self.failUnless(self.p("<parent><child/></parent>"))

    def testPassWithMultipleChildren(self):
        "XCheck() accepts multiple copies of one child if child.max_occurs allows"
        self.p.children[0].max_occurs= 2
        self.failUnless(self.p("<parent><child/><child/></parent>"))

    def testPassWithSequentialChildren(self):
        "XCheck() accepts a sequence of children"
        self.p.add_child(self.m)
        self.failUnless(self.p("<parent><child/><kid/><kid/></parent"))

    def testPassWithGrandChildren(self):
        "XCheck() accepts multiple levels of children"
        self.p.children[0].add_child(self.m)
        self.failUnless(self.p("<parent><child><kid/><kid/></child></parent>"))

    def testFailWithUnexpectedChildren(self):
        "XCheck() raises UnexpectedChildError if element has children and checker expects none"
        t = XCheck('check', check_children = True)
        self.assertRaises(UnexpectedChildError, t, "<check><unwanted/></check>")

    def testIgnoreChildren(self):
        "XCheck() should ignore children if told"
        t = XCheck('check', check_children = False)
        self.failUnless(t("<check><unexpected/></check>"),
            "XCheck checked children even when told not to")
        self.failUnless(self.p("<parent><unexected/></parent>",
            check_children = False),
            "XCheck checked children at call when told not to")

    def testFailUnknownChild(self):
        "XCheck() fails with unknown child"
        self.assertRaises(self.p.error, self.p, "<parent><mystery/></parent>")

    def testFailWithExtraChild(self):
        "XCheck() fails with more children elements than checker.max_occurs allows"
        self.assertRaises(UnexpectedChildError, self.p,
            "<parent><child/><child/></parent>")

    def testFailWithMissingChild(self):
        "XCheck() fails if a required child is missing"
        self.assertRaises(MissingChildError, self.p, "<parent/>")

    def testAcceptOptionalChild(self):
        "XCheck() accepts an optional child"
        self.p.children[0].min_occurs= 0
        self.failUnless(self.p('<parent/>'),
            "XCheck cannot handle optional child")
        self.failUnless(self.p('<parent><child/></parent>'),
            "XCheck cannot handle an optional child that exists")

    def testAcceptOptionalChild2(self):
        "XCheck() accepts an optional child that is not the first child"
        self.m.min_occurs = 0
        self.p.add_child(self.m)
        self.failUnless(self.p('<parent><child/></parent'),
            "XCheck cannot handle an optional child that is not the first")
        self.failUnless(self.p('<parent><child/><kid/></parent>'), "Oops")

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
        self.failUnless(self.t('english@spiritone.com'))

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

class IntCheckTC(unittest.TestCase):
    "These test if the defaults are created properly"
    def setUp(self):
        self.t = IntCheck('test', min=1, max = 10)
    def tearDown(self):
        del self.t

    #~ valid input tests
    def testPassWithInt(self):
        "IntCheck() accepts in-bounds integer"
        self.failUnless(self.t( 9))

    def testPassWithValidString(self):
        "IntCheck() accepts integer-equivalent string"
        self.failUnless(self.t( '6'))

    def testPassWithValidFloat(self):
        "IntCheck() accepts with integer-equivalent float"
        self.failUnless(self.t( 6.0 ) )

    def testPassWithElement(self):
        "IntCheck() accepts valid element.text"
        self.failUnless(self.t(ET.fromstring('<test>4</test>')))

    def testPassWithXML(self):
        "IntCheck() accepts valid xml strings"
        self.failUnless(self.t('<test>4</test>'))

    #~ bad input tests
    def testFailWithEmptyString(self):
        "IntCheck() raises ValueError when passed an empty string when required"
        self.assertRaises(ValueError, self.t, '')

    def testFailWithOOBInt(self):
        "IntCheck() fails with out-of-bounds integer"
        self.assertRaises(self.t.error, self.t, -4)

    def testFailWithFloat(self):
        "IntCheck() raises TypeError when passed with non-integral float"
        self.assertRaises(TypeError, self.t, 5.6)

    def testFailWithOOBString(self):
        "IntCheck() fails with out-of-bounds integral string"
        self.assertRaises(self.t.error, self.t, '45')

    def testFailWithFloatString(self):
        "IntCheck() fails when passed float-equivalent string"
        self.assertRaises(ValueError, self.t, '5.6')

    def testFailWithFloatElem(self):
        "IntCheck() raises ValueError with element.text as non-integral float"
        self.assertRaises(ValueError, self.t, ET.fromstring('<test>5.5</test>') )

    def testFailWithFloatElemString(self):
        "IntCheck() fails with xml-formatting string as non integral float"
        self.assertRaises(ValueError, self.t, '<test>5.4</test>')

    def testFailWithOOBElement(self):
        "IntCheck() fails with element.text as out-of-bounds integer"
        self.assertRaises(self.t.error, self.t, ET.fromstring('<test>99</test>'))

    def testFailWithOOBElementString(self):
        "IntCheck() fails with xml-formattet sting with out of bounds integer"
        self.assertRaises(self.t.error, self.t, '<test>99</test>')

    def testFailWithNonInteger(self):
        "IntCheck() fails with a non-integer"
        self.assertRaises(ValueError, self.t, 'a')

    def testNormalization(self):
        self.assertEqual(self.t('9', normalize=True), 9,
            "IntCheck normalized bunged a string")
        self.assertEqual(self.t(9, normalize=True), 9,
            "IntCheck normalize bunged an integer")

class SelectionCheckTC(unittest.TestCase):
    def setUp(self):
        self.s = SelectionCheck('choice', values=['alpha','beta','gamma'])

    def tearDown(self):
        del self.s

    def testDefaultAttributes(self):
        "SelectionCheck creates appropriate default attrubutes"
        self.assertTrue(self.s.ignore_case, "ignore_case not True")

    def testCustomAttributes(self):
        "SelectionCheck customizes attributes"
        s = SelectionCheck('choice', values=['a', 'b'], ignore_case = False)
        self.assertFalse(s.ignore_case, "ignore_case not customized")

    def testFailWithoutValues(self):
        "SelectionCheck raises NoSelectionError if not given any values"
        self.assertRaises(NoSelectionError, SelectionCheck, 'choices')

    def testFailWithEmptyListForValues(self):
        "SelectionCheck raises NoSelectionError if values is an empty list"
        self.assertRaises(NoSelectionError, SelectionCheck, 'choices', values = [])

    def testFailWithNonListForValues(self):
        "SelectionCheck() raises BadSelectionsError if values is not iterable"
        self.assertRaises(BadSelectionsError, SelectionCheck, 'choices', values=None)

    def testFailWithNonCaseSensitiveChoice(self):
        "SelectionCheck() fails if case doesn't match and ignore_case is False"
        self.s.ignore_case = False
        self.assertRaises(self.s.error, self.s, 'Alpha')

    def testPassWithNonCaseSensitiveChoice(self):
        "SelectionCheck() accepts value in list without case match and caseSensitive is False"
        self.s.ignore_case = True
        self.failUnless(self.s('Alpha'))

    def testPassWithElementText(self):
        "SelectionCheck() accepts appropriate xml-formmated text"
        self.failUnless(self.s('<choice>alpha</choice>'))

    def testPassWithElement(self):
        "SelectionCheck() accepts appropriate element.text"
        self.failUnless(self.s(ET.fromstring('<choice>alpha</choice>')))

    def testFailWithOutOfListValue(self):
        "SelectionCheck() fails if value not in list of acceptable values"
        self.assertRaises(self.s.error, self.s, 'delta')

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

    def testas_string(self):
        self.assertEqual(self.b('yes', as_string=True), 'True')
        self.assertEqual(self.b('NO', as_string=True), 'False')



class ListCheckTC(unittest.TestCase):
    "random doc string"
    def setUp(self):
        self.l = ListCheck('letter', values=['alpha','gamma','delta'])

    def tearDown(self):
        del self.l

    def testSingleValidString(self):
        "ListCheck accepts a valid list of length 1"
        self.failUnless(self.l("alpha"))

    def testFailWithOutOfValueItem(self):
        'ListCheck fails if an item in the list is not in value list'
        self.assertRaises(self.l.error, self.l, "alpha, beta")

    def testFailWithDuplicateItems(self):
        "ListCheck fails with duplicated values and allowDuplicates is False"
        self.l.allowDuplicates = False
        self.assertRaises(self.l.error, self.l, "alpha, alpha")

    def testPassWithDuplicateItems(self):
        "ListCheck accepts duplicates if allowDuplicates is True"
        self.l.allow_duplicates = True
        self.failUnless(self.l('alpha, alpha'))

    def testFailIfTooManyItems(self):
        "ListCheck fails if list has too many items"
        self.l.max_items = 2
        self.assertRaises(self.l.error, self.l, 'alpha, delta, gamma')

    def testFailIfTooFewItems(self):
        "ListCheck fails if list has too few items"
        self.l.min_items = 2
        self.assertRaises(self.l.error, self.l, 'delta')

    def testFailIfWrongCase(self):
        "ListCheck fails if wrong case and ignore_case is False"
        self.l.ignore_case = False
        item ='alpha, gamma, delta'
        self.assertRaises(self.l.error, self.l, item.upper()  )
        self.assertRaises(self.l.error, self.l, item.title() )

    def testPassEvenWithWrongCase(self):
        "ListCheck accpets items if wrong case and ignore_case is True"
        self.l.ignore_case = True
        item ='alpha, gamma, delta'
        self.failUnless( self.l(item.upper()) )
        self.failUnless( self.l(item.title()) )

    def testPassWithAlternateDelimiter(self):
        "ListCheck accepts alternate deliminator"
        self.l.delimiter="::"
        self.failUnless(self.l("alpha::gamma:: delta") )

    def testPassWithEmptyValues(self):
        "ListCheck() accepts anything if the value list is empty"
        l = ListCheck('anythinggoes', values = [])
        self.failUnless(l("alpha, beta, gamma"), "ListCheck demands values")

    def testAcceptEmptyList(self):
        "ListCheck() accepts an empty list if minitems is 0"
        self.failUnless(self.l('<letter/>'), "ListCheck cannot handle empty list")

    def testNormalizedValue(self):
        self.assertEqual(['alpha', 'gamma'] , self.l("alpha, gamma", normalize=True))

    def testNormalizedList(self):
        self.assertEqual('alpha, gamma', self.l("alpha, gamma", as_string=True) )
        self.assertEqual('alpha, gamma', self.l("<letter>alpha, gamma</letter>", as_string=True))

    def testAcceptsPythonList(self):
        self.assertEqual('alpha, gamma', self.l(['alpha', 'gamma'], as_string=True) )

    def testDummyValue(self):
        self.assertEqual(self.l.dummy_value(), "")
        self.l.min_items = 1
        self.assertEqual(self.l.dummy_value(), "alpha")
        self.l.min_items = 2
        self.assertEqual(self.l.dummy_value(), "alpha,gamma")

    def testDummyValue2(self):
        self.l.values=[]
        self.assertEqual(self.l.dummy_value(), "")
        self.l.min_items = 1
        self.assertEqual(self.l.dummy_value(), "a")
        self.l.min_items = 2
        self.assertEqual(self.l.dummy_value(), "a,b")

class DateTimeCheckTC(unittest.TestCase):
    def setUp(self):
        self.d = DateTimeCheck('date')

    def tearDown(self):
        del self.d

    def testDefaults(self):
        "DateTimeCheck creates appropriate default values"
        self.assertFalse(self.d.allow_none, "allow_none not False")
        self.assertEqual(self.d.format, "%a %b %d %H:%M:%S %Y", "format not the default")
        self.assertEqual(self.d.formats, [], "formats not an empty list")

    def testCustomizedAttributes(self):
        "DateTimeCheck customizes attrbutes"
        d = DateTimeCheck('date', allow_none=True, format="%b-%d-%Y",
            formats = ['%d-%m-%Y',])
        self.assertTrue(d.allow_none, "allow_none not customized")
        self.assertEqual(d.format, '%b-%d-%Y', 'format not customised')
        self.assertEqual(d.formats, [ '%d-%m-%Y'])

    def testDefaultFormat(self):
        "DateTimeCheck() accepts the default datetime"
        self.failUnless(self.d('Mon Oct 26 22:20:43 2009'), "cannot parse default date")

    def testCustomFormat(self):
        "DateTimeCheck() accepts a custom format"
        d = DateTimeCheck('test', format="%Y%m%d%H%M%S")
        self.failUnless(d('20090101122042'), 'cannot parse custom date')

    def testDateTimeObject(self):
        "DateTimeCheck() returns a datetime.datetime object when requested"
        dt = self.d("Mon Oct 26 14:52:42 2009", as_datetime=True)
        self.assertTrue(isinstance(dt, datetime.datetime), "Did not return a datetime.datetime object")

    def testTimeStructObject(self):
        "DateTimeCheck() returns a time.struct_time object when requested"
        dt = self.d("Mon Oct 26 09:00:00 2009", as_struct=True)
        self.assertTrue(isinstance(dt, time.struct_time), "Did not return a time.struct_time object")

    def testTimeStringResult(self):
        "DateTimeCheck() returns a string by default"
        dt = self.d("Sat Jul 14 11:00:00 2001")
        self.assertTrue(isinstance(dt, basestring), "Did not return a string by default")

    def testBooleanResult(self):
        "DateTimeCheck() return a boolean if all _asXXX options are false"
        dt = self.d("Sat Jul 14 11:00:00 2001", as_string = False)
        self.assertTrue(isinstance(dt, bool), "Did not return a boolean")

    def testDateOutOfBounds(self):
        "DateTimeCheck() fails if date is out of range"
        d = DateTimeCheck('test', format="%m/%d/%Y", minDateTime = "10/1/2009", maxDateTime = "10/31/2009")
        self.assertRaises(self.d.error, d, "9/30/2009")

    def testMonthAndDayOnly(self):
        "DateTimeCheck() accepts month and day only"
        d = DateTimeCheck('mday', format="%b %d", minDateTime="Oct 10", maxDateTime="Oct 20")
        self.failUnless(d('Oct 12'), "Cannot accept month and day only")
        self.assertRaises(d.error, d, 'Oct 9')
        self.assertRaises(d.error, d, 'Nov 1')

    def testFormatLists(self):
        "DateTimeCheck() handles a list of formats"
        d = DateTimeCheck('formatlist', formats=['%b %d', '%b %d %Y'])
        self.failUnless(d('Oct 1'), "DateTimeCheck() cannot handle the first format")
        self.failUnless(d('Jan 1 2000'), "DateTimeCheck() cannot handle the second format")

    def testAllowNone(self):
        "DateTimeCheck() allows None, optionally"
        d = DateTimeCheck('date', allow_none = True)
        self.failUnless(d('None'), "Fails to accept string None")
        self.failUnless(d(None), "Fails to accept None type")
        self.failUnless(d('<date>None</date>'), "Fails to accept string-node")
        self.failUnless(d('<date>none</date>'), "Fails to accept 'none' as node text")
        self.failUnless(d('none'), "Fails to accept 'none' as text")

class RenameTC(unittest.TestCase):
    def testRename(self):
        "_rename creates object with given name"
        x = XCheck('original')
        y = x._rename('copy')
        self.assertEqual(y.name, 'copy')

    def testNoBackFuck(self):
        "_rename doesn't change the name of the original item"
        x = XCheck('original')
        y = x._rename('copy')
        self.assertEqual(x.name, 'original')

    def testStandardObjectAtts(self):
        "_rename should copy all the standard object atts"
        x = XCheck('original', min_occurs=3, max_occurs=5, unique=True,
            required=False,  check_children=False, ordered=False)
        y = x._rename('copy')
        for att in ['min_occurs', 'max_occurs', 'children', 'unique',
            'required', 'attributes', 'error', 'check_children', 'ordered']:
            self.assertEqual(getattr(x, att), getattr(y, att), "%s not equal" % att)

    def testLeaveChildrenBehind(self):
        "_rename should create a copy with same children"
        child = TextCheck('child')
        parent = XCheck('parent', children=[child])
        copy = parent._rename('copy')
        self.assertEqual(copy.children, [child])

class DummyTC(unittest.TestCase):
    def test_not_xcheck(self):
        for ch in [TextCheck, IntCheck, DecimalCheck, EmailCheck, IntCheck, SelectionCheck]:
            self.assertRaises(TypeError, ch.dummy_element, "%s made a dummy" % ch.name)

    def test_make_dummy(self):
        text = TextCheck('text', min_length=4)
        email = EmailCheck('email')
        Int = IntCheck('int', minValue = NINF)
        selection = SelectionCheck('select', values = ['one', 'two', 'three'])
        Bool = BoolCheck('bool')
        List = ListCheck('list', values = ['a','b','c','d','e'], min_items = 3)

        ch = XCheck('checker', children = [text, email, Int, selection, Bool, List])

        d = ch.dummy_element()

        self.assertEqual(d.find('text').text, 'ABCD', "TextCheck didn't create default")
        self.assertEqual(d.find('int').text, '0', "IntCheck didn't create dummy")


class XWrapTC(unittest.TestCase):
    def setUp(self):
        nick = BoolCheck('nick', required=False)
        fname = TextCheck('first', min_length = 1)
        fname.addattribute(nick)

        lname = TextCheck('last', min_length = 1)
        code = IntCheck('code', min_occurs = 1, max_occurs = 5)
        code.addattribute(TextCheck('word', required=False) )
        ch = XCheck('name', children=[fname, lname, code])
        idch = IntCheck('id', required=True)
        ch.addattribute(idch)
        elem = ET.fromstring("""<name id="1">
        <first nick="true">Josh</first>
        <last>English</last>
        <code>12</code>
        <code word="answer">42</code>
        </name>""")
        self.w = Wrap(ch, elem)

    def tearDown(self):
        del self.w

    ## New 0.4.7
    def test_direct_access(self):
        self.assertEqual(self.w.first, "Josh")
        self.assertEqual(self.w.last, "English", "Last Name didn't match")
        self.assertEqual(self.w.code, ['12','42'], "Code didn't return a list")

    def test_bad_init(self):
        "Wrap should fail on initiation if element doesn't validate by checker"
        ch = TextCheck('name')
        elem = ET.fromstring('<idea>name</idea>')
        self.assertRaises(XCheckError, Wrap, ch, elem)

#### _get_elem_value
    def test_bad_xml_tag(self):
        "_get_elem_value(tag) should fail if the tag is not part of the checker definition"
        self.assertRaises(ValueError, self.w._get_elem_value, 'pp')

    def test__get_elem_value(self):
        "_get_elem_value(tag) should return appropriate text"
        self.assertEqual(self.w._get_elem_value('first'), 'Josh')
        self.assertEqual(self.w._get_elem_value('last'), 'English')

    def test_get_list_elem_text(self):
        "get_list_elem_value() returns appropriate value"
        self.assertEqual(self.w._get_elem_value('code', 0), 12)
        self.assertEqual(self.w._get_elem_value('code', 1), 42)

    def test_get_elem_text(self):
        "_get_elem_value(tag) should return a string if _normalize is false"
        self.assertEqual(self.w._get_elem_value('code', 0, False), '12')

    def test_get_list_elem_bad_index(self):
        "_get_elem_value() fails if index is beyond current availability in the node"
        self.assertRaises(IndexError, self.w._get_elem_value, 'code', 2)

    def test_get_list_elem_bad_index2(self):
        "_get_elem_value fails if index in out of bounds by checker definition"
        self.assertRaises(IndexError, self.w._get_elem_value, 'code', 6)

    def test_get_list_elem_bad_index_type(self):
        self.assertRaises(TypeError, self.w._get_elem_value, 'code', 'a')
        self.assertRaises(TypeError, self.w._get_elem_value, 'code', 1.5)

##### _set_elem_value
    def test_get_wrong_elem_att(self):
        "_get_elem_att(name, att) should fail if att not an attribute of name element according to checker definition"
        self.assertRaises(ValueError, self.w._get_elem_att, 'last', 'nick')

    def testBadSetValue(self):
        "set_elem_text(tag, value) should fail if value is not valid by the checker"
        self.assertRaises((ValueError, XCheckError), self.w._set_elem_value, 'last', '')

    def test_set_list_elem_value_no_index(self):
        "_set_elem_value(tag, value) should work with no index given"
        self.w._set_elem_value('first', 'Stephanie')
        self.assertEqual(self.w._get_elem_value('first'), 'Stephanie')

    def test_set_list_elem_text_default_index(self):
        "_set_elem_value() should change the default index"
        self.w._set_elem_value('code', 9)
        self.assertEqual(self.w._get_elem_value('code'), 9)

    def test__set_elem_value_only_one_value(self):
        "_set_elem_value() should not change other index values"
        self.w._set_elem_value('code', '9')
        self.failUnlessEqual(self.w._get_elem_value('code', 1), 42)

    def test_set_list_elem_text_by_index(self):
        self.w._set_elem_value('code', '9', 1)
        self.failUnlessEqual(self.w._get_elem_value('code', 1), 9)

    def test_set_list_elem_text_bad_input(self):
        self.failUnlessRaises((ValueError, XCheckError),
            self.w._set_elem_value, 'code', 'alpha' )

    def test_set_list_elem_text_index_too_high(self):
        "_set_elem_value fails if the index is greater than checker max_occurs"
        self.failUnlessRaises(IndexError,
            self.w._set_elem_value, 'first', 'Stephanie', 1)
#### _get_elem_att
    def test__get_elem_att(self):
        "_get_elem_att(name, att) should return attribute value or None"
        self.assertEqual(self.w._get_elem_att('first','nick'), True)

    def test__get_elem_att_by_index(self):
        self.assertEqual(self.w._get_elem_att('code', 'word'), None)
        self.assertEqual(self.w._get_elem_att('code', 'word', 1), 'answer')

    def test__get_elem_att_by_out_of_bounds_index(self):
        "_get_elem_att() should fail if index is larger than definition allows"
        self.failUnlessRaises(IndexError,
            self.w._get_elem_att, 'code', 'word', 6)

    def test__get_elem_att_with_too_high_index(self):
        "_get_elem_att() should fail if index is larger than current elements"
        self.failUnlessRaises((IndexError, XCheckError),
            self.w._get_elem_att, 'code', 'word', 3)


### _set_elem_att
    def test__set_elem_att(self):
        "_set_elem_att works for valid input"
        self.w._set_elem_att('first', 'nick', False)
        self.assertEqual(self.w._get_elem_att('first', 'nick'), False)


    def test__set_elem_att_by_index(self):
        "_set_elem_att() sets the valid index"
        self.w._set_elem_att('code','word', 'test', 1)
        self.failUnlessEqual(self.w._get_elem_att('code', 'word',1), 'test')

### _add_elem
    def test__add_elem_when_plain_text(self):
        "_add_elem() should work for simple node creation values"
        self.w._add_elem('code', 64, {'word': 'old'})
        self.failUnlessEqual(self.w._get_elem_value('code', 2), 64)
        self.failUnlessEqual(self.w._get_elem_att('code', 'word', 2),'old')

    def test__add_elem_no_more_allowed(self):
        "_add_elem() should fail if the number of elements has reached checker.max_occurs"
        self.w._add_elem('code', 2)
        self.w._add_elem('code', 3)
        self.w._add_elem('code', 4) #! These should be fine
        self.failUnlessRaises(IndexError, self.w._add_elem, 'code', 5)

### miscellaneous

    def test_get_optional_elem_value(self):
        ch = XCheck('thing')
        ch.add_child(TextCheck('item', min_occurs = 0))

        elem = ET.Element('thing')

        w = Wrap(ch, elem)

        self.assertEqual(w._get_elem_value('item'), '')

    def test_get_att(self):
        self.assertEqual(self.w._get_att('id'), 1)

    def test_set_att(self):
        self.w._set_elem_att('name','id', 2)
        self.assertEqual(self.w._get_att('id'), 2,
            "Didn't change element attribute")

class XChildWrapTC(unittest.TestCase):
    def setUp(self):
        #~ dude = XCheck('dude')
        nick = BoolCheck('nick', required=False)
        fname = TextCheck('first', min_length = 1)
        fname.addattribute(nick)



        lname = TextCheck('last', min_length = 1)
        code = IntCheck('code', min_occurs = 1, max_occurs = 5)
        code.addattribute(TextCheck('word', required=False) )
        name = XCheck('name', children=[fname, lname, code])

        emailtype = SelectionCheck('type', values = ['home','work', 'personal'])
        email = EmailCheck('email', max_occurs=2)
        email.addattribute(emailtype)
        street = TextCheck('street')
        city = TextCheck('city')

        address = XCheck('address', children = [street, city, email], max_occurs = 4)
        self.address = address
        dude = XCheck('dude', children=[name, address])
        idch = IntCheck('id', required=True)
        dude.addattribute(idch)

        elem = ET.fromstring("""<dude id="1">
        <name>
            <first nick="true">Josh</first>
            <last>English</last>
            <code>12</code>
            <code word="answer">42</code>
        </name>
        <address>
            <street>100 Main St</street>
            <city>Podunk</city>
            <email type="home">dude@example.com</email>
            <email type="work">dude@slavewage.com</email>
        </address>
        <address>
            <street>318 West Nowhere Ln</street>
            <city>East Podunk</city>
            <email type="personal">dude@home.net</email>
        </address>
        </dude>""")
        self.w = Wrap(dude, elem)

    def tearDown(self):
        del self.w


    def test__get_child_Wrap(self):
        "_get_child_Wrap returns a Wrap instance with the appropriate checker and node"
        w0 = self.w._get_child_wrap('address', 0)
        w1 = self.w._get_child_wrap('address', 1)
        self.assertEqual(w0._checker, self.address, "checker object is wrong")
        self.assertEqual(w0._elem.tag, "address", "element tag is wrong")
        self.assertEqual(w0._get_elem_value('street'), '100 Main St', "sub element value misread")
        self.assertEqual(w1._get_elem_value('street'), '318 West Nowhere Ln')

class DummyValueTC(unittest.TestCase):
    def test_datetimedummy(self):
        "DateTimeCheck.dummy_value() should return the minimum date"
        import datetime
        mindate = datetime.datetime.min.replace(year=1900)
        d = DateTimeCheck('name')
        self.assertEqual(mindate.strftime(d.format), d.dummy_value())

    def test_intdummy(self):
        "IntCheck.dummyValue() should return the string min value or '0'"
        i = IntCheck('things')
        self.assertEqual('0', i.dummy_value(), "IntCheck not returning 0 by default")
        i = IntCheck('things', min = 2)
        self.assertEqual('2', i.dummy_value(), "IntCheck.dummy_value() not returning custom minimum value")

    def test_selectiondummy(self):
        "SelectionCheck.dummyValue() should return the first option"
        s = SelectionCheck('things', values=['one', 'two', 'three'])
        self.assertEqual(s.dummy_value(), "one")



class TokensTC(unittest.TestCase):
    def setUp(self):
        self.ch = dude

    def tearDown(self):
        del self.ch

    def test_tokenlist(self):
        tokens = self.ch.tokens()
        tlist =['dude', 'id', 'nick', 'first', 'last', 'code', 'word', 'name',
            'type', 'email', 'street', 'city', 'address']

        self.assertItemsEqual(tokens, tlist)

    def test_path_to(self):
        tokens =self.ch.tokens()
        for tk in tokens:
            nm, at = self.ch.path_to(tk)
            self.assertTrue(not(nm is None and at is None), "path_to returned (None,None) for %s" % tk)

    def test_find_all(self):
        for tk in self.ch.tokens():
            nm, at = self.ch.path_to(tk)
            if at is None:
                nd = list(dudeNode.findall(nm))
            else:
                nd = list(dudeNode.findall("%s[@%s]" % (nm, at)))
            self.assertTrue(len(nd) > 0, "node.findall didn't find %s" % tk)
            for n in nd:
                self.assertTrue(ET.iselement(n))
            ### This tests that element objects were found
            ### cannot test if it is the right node because attributes are included in tokens()

    def test_find_children(self):
        for tk in ['dude', 'first', 'last', 'code', 'name', \
             'email', 'street', 'city', 'address']:
            pth = self.ch.xpath_to(tk)
            for nd in dudeNode.findall(pth):
                self.assertTrue(nd.tag == tk)

_toDictListChecks= (
    ('<item>one</item>',   {'item':['one']} ),
    ('<item>two</item>',   {'item':['two']} ),
    ('<item>three</item>', {'item':['three']} ),
    ('<item>one, two</item>', {'item': ['one', 'two']} ),
    )
class ToDictTC(unittest.TestCase):
    def test_text(self):
        "Test a simple text object without attributes"
        ch = TextCheck('name')
        node = ET.fromstring('<name>Josh</name>')
        self.assertEqual(type(ch.to_dict(node)), dict, "to_dict did not create a dictionary")
        self.assertDictEqual({'name':'Josh'}, ch.to_dict(node), "to_dict did not create teh right dictionary")

    def test_bool(self):
        ch = BoolCheck('valid')
        node = ET.fromstring('<valid>True</valid>')
        self.assertDictEqual({'valid':True}, ch.to_dict(node), "to_dict did not create the right boolean value")

    def test_selection(self):
        "Selection Check translates to a string value"
        ch = SelectionCheck('item', values=['one', 'two', 'three'])
        node = ET.fromstring('<item>one</item>')
        self.assertDictEqual({'item': 'one'}, ch.to_dict(node))

    def test_list(self):
        "ListCheck returs a list of strings"
        ch = ListCheck('item', values=['one', 'two', 'three'])
        for string, dictionary in _toDictListChecks:
            node = ET.fromstring(string)
            self.assertDictEqual(dictionary, ch.to_dict(node))

    def test_int(self):
        ch = IntCheck('item')
        node = ET.fromstring('<item>1</item>')
        self.assertDictEqual({'item': 1}, ch.to_dict(node) )

    ### 'thing':None exists because there are no children to this attribute
    def test_attribute(self):
        ch = XCheck('thing')
        ch.addattribute(BoolCheck('open'))
        node = ET.fromstring('<thing open="True" />')
        self.assertDictEqual({'thing.open': True, 'thing':None}, ch.to_dict(node))

    def test_text_with_attribute(self):
        ch = TextCheck('name')
        ch.addattribute(BoolCheck('unique'))
        node = ET.fromstring('<name unique="False">Josh</name>')
        self.assertDictEqual({'name':'Josh', 'name.unique':False}, ch.to_dict(node))

    def test_with_children(self):
        ch = XCheck('name')
        ch.add_children(TextCheck('first'), TextCheck('last'))
        node = ET.fromstring('<name><first>Josh</first><last>English</last></name>')
        self.assertDictEqual({'first':'Josh', 'last':'English'}, ch.to_dict(node))

    def test_dudeToDict(self):
        D = dude.to_dict(dudeNode)
        self.assertEqual(D['address'][0]['city'],'Podunk', "to_dict did not create a subdictionary properly")
        self.assertEqual(D['address'][0]['street'], '100 Main St')
        self.assertEqual(D['address'][0]['email'][0]['email'], 'dude@example.com')
        self.assertEqual(D['address'][0]['email'][0]['email.type'], 'home')
        self.assertEqual(D['address'][0]['email'][1]['email'], 'dude@slavewage.com')
        self.assertEqual(D['address'][0]['email'][1]['email.type'], 'work')
        self.assertEqual(D['address'][1]['city'], 'East Podunk')
        self.assertEqual(D['address'][1]['street'], '318 West Nowhere Ln')
        self.assertEqual(D['address'][1]['email'][0]['email'], 'dude@home.net')
        self.assertEqual(D['address'][1]['email'][0]['email.type'], 'personal')
        self.assertEqual(D['name']['first'], 'Josh')
        self.assertEqual(D['name']['last'], 'English')
        self.assertEqual(D['name']['first.nick'], True)
        self.assertEqual(D['name']['code'][0]['code'], 12)
        self.assertEqual(D['name']['code'][1]['code'], 42)
        self.assertEqual(D['name']['code'][1]['code.word'], 'answer')

class FromDictTC(unittest.TestCase):
    def test_text(self):
        ch = TextCheck('name')
        node = ch.from_dict( {'name':'Josh'} )
        self.assertEqual(node.tag, 'name', "from_dict created the wrong tag")
        self.assertEqual(node.text, 'Josh', 'from_dict added wrong text')

    def test_bool(self):
        ch = BoolCheck('open')
        node = ch.from_dict( {'open': True} )
        self.assertEqual(node.text, 'True', 'from_dict added wrong text in boolean')
        self.assertTrue(ch(node), "node did not validate")

    def test_text_with_attribute(self):
        ch = TextCheck('name')
        ch.addattribute(BoolCheck('unique'))
        node = ch.from_dict({'name.unique':True, 'name':'Josh'})
        self.assertEqual(node.text, 'Josh')
        self.assertEqual(node.get('unique'), 'True')
        self.assertTrue(ch(node), 'node did not validate')

    def test_list(self):
        ch = ListCheck('name', values=['John', 'Mary', 'Joseph', 'Joshua'])
        node = ch.from_dict({'name':'John, Mary'})
        self.assertEqual(node.text, "John, Mary", "from_dict didn't accept a list formatted string")
        node = ch.from_dict({'name': ['Joseph', 'Joshua']})
        self.assertEqual(node.text, "Joseph, Joshua", "from_dict didn't accept a list")
        self.assertTrue(ch(node), "node did not validate")

    def test_optional_child(self):
        ch = XCheck('name')
        ch.add_children(TextCheck('first'), TextCheck('nick', min_occurs=0))
        self.assertTrue(ch(ch.from_dict({'first':'Josh'})))
        self.assertTrue(ch(ch.from_dict({'first':'Josh','nick':'asshat'})))

class LoaderTC(unittest.TestCase):


    def test_xcheck_defaults(self):
        ch = load_checker('<xcheck name="person" />')
        self.assertTrue(isinstance(ch, XCheck))
        self.assertEqual(ch.name, 'person', "load_checker() did not set name")
        self.assertEqual(ch.min_occurs, 1, "load_checker() did not set min_occurs default")
        self.assertEqual(ch.max_occurs, 1, "load_checker() did not set max_occurs default")
        self.assertEqual(ch.children, [], "load_checkr() did not create empty children default")
        self.assertFalse(ch.unique, "load_checker() did not create default unique attribute")
        self.assertTrue(ch.required)
        self.assertEqual(ch.error, XCheckError)
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
        self.assertIsInstance(ch, DateTimeCheck)

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

    def test_dude(self):
        dude_def = dude.to_definition_node()
##        indent(dude_def)
##        ET.dump(dude_def)
        new_ch = load_checker(dude_def)
        new_ch(dudeNode)

    def test_load_errors(self):
        ch = load_checker("<text name='oops' error='TypeError' />")
        self.assertTrue(issubclass(ch.error, XCheckError))

class TestWrap3(unittest.TestCase):
    def test_wrap_string(self):
        s = "<dude><first>Josh</first><last>English</last></dude>"
        dudecheck = load_checker(
            """<xcheck name='dude'>
            <children>
            <text name='first'/>
            <text name='last'/>
            </children>
            </xcheck>
            """)
        dudecheck(s)
        dude = Wrap(dudecheck)
        self.assertTrue(isinstance(dude, Wrap))
        dude = Wrap(dudecheck, s)
        self.assertTrue(isinstance(dude, Wrap))
        self.assertEqual(dude._get_elem_value('first'),'Josh')

    def test_add_elem_if_needed(self):
        stuff_check = load_checker(
            """<xcheck name="stuff">
            <children>
            <text name="item" min_occurs="0" max_occurs="4" />
            </children>
            </xcheck>
            """)
        empty_example = Wrap(stuff_check)
        empty_example._set_elem_value('item','one')

        self.assertEqual(empty_example._get_elem_value('item'),'one')

if __name__=='__main__':
    import xcheck
    print xcheck
    unittest.main(verbosity=0)
