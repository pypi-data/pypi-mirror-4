from functools import partial

from core import ET
from utils import get_elem

class Wrap(object):
    """Wrap(checker, element)
    Creates a object Wrapper around an element that must validate to the
    checker object.

    :param checker: an XCheck instance. Should not be an instance of a sub-class
    :type checker: XCheck
    :param element: Data to be wrapped
    :type element: ElementTree.Element, a string representation, or None

    """
    def __init__(self, ch, elem=None):
        ch(elem)
        self._checker = ch
        if elem is None:
            elem = ch.dummy_element()
        else:
            elem = get_elem(elem)
        self._elem = elem

    def _get_att(self, att_name, normalize=True):
        """_get_att(name, [normalize=True]
        Return the value of the node attribute"""
        if att_name not in self._checker.tokens():
            raise ValueError, "%s is not a valid attribute name" % att_name

        attcheck = self._checker.get(att_name)

        return attcheck(self._elem.get(att_name), normalize=normalize)

    def _get_elem_value(self, tag_name, nth = 0, normalize=True):
        """get_list_elem_text(tag_name, nth, normalize)
        Return the text value of the nth occurence of the element tag_name.
        nth is a zero-based index.

        Uses the specific xcheck object, so an IntCheck checker will
        return a normalized (i.e., integer) value

        If normalize is False, returns the text value as it appears
        """
        if tag_name not in self._checker.tokens():
            raise ValueError("Invalid tag name by checker: %s" % tag_name)

        childcheck = self._checker.get(tag_name)

        # if nth isn't a valid number this will raise a type error
        if nth >= childcheck.max_occurs:
            raise IndexError("index %d too high by checker" % nth)

        children = list(self._elem.findall('.//%s' % tag_name) )
        if len(children) == 0 and childcheck.min_occurs ==0:
            return ''
        if nth >= len(children):
            raise IndexError("index %d out of range of children" % nth)

        elist = list(self._elem.findall('.//%s' % tag_name))

        # if nth isn't a valid integer this will raise a type error
        if normalize:
            return childcheck(elist[nth].text, normalize=normalize)
        else:
            return elist[nth].text

    def _set_elem_value(self, tag_name, value, nth = 0):
        """_set_elem_value(self, tag_name, value, nth = 0)
        Sets the nth occurance of element tag_name.text to value

        Value will be converted to a string.
        """
        if tag_name not in self._checker.tokens():
            raise ValueError("%s is not a valid tag in the checker" % tag_name)

        childcheck = self._checker.get(tag_name)

        if nth >= childcheck.max_occurs:
            raise IndexError("index %d out of checker bounds" % nth)

        children = list(self._elem.findall('.//%s' % tag_name) )

        if len(children) == 0 and childcheck.min_occurs==0:
            self._add_elem(tag_name, value)
            children = list(self._elem.findall('.//%s' % tag_name) )

        if nth >= len(children):
            raise IndexError, "index %d out of range of children" % nth

        childcheck(value)

        children[nth].text = str(value)


    def _get_elem_att(self, tag, att, nth=0, normalize=True):
        """_get_elem_att(tag, att)
        returns the attribute value for the given tag.
        """
        if tag not in self._checker.tokens():
            raise ValueError("'%s' is not a valid element tag" % tag)
        if att not in self._checker.tokens():
            raise ValueError("'%s' not a valid attribute name" % (att))

        tagcheck = self._checker.get(tag)
        if att not in tagcheck.attributes:
            raise ValueError("'%s' not an attribute of '%s'" % (att, tag))

        if nth >= tagcheck.max_occurs:
            raise IndexError("Index %d out of checker bounds" % nth)

        attcheck = self._checker.get(att)

        elist = list(self._elem.findall('.//%s' % tag))
        if elist == [] and tag == self._elem.tag:
            elem = self._elem
        else:
            elem = elist[nth]

        if elem.get(att) is None:
            return None
        else:
            return attcheck(elem.get(att), normalize=normalize)
        #~ return elem.get(att)

    def _set_elem_att(self, tag, att, value, nth = 0):
        """_set_elem_att(tag, att, value, nth=0)
        Sets the attribute value for the nth occurance given element tag.
        Raises a ValueError if any of the following are true::

            * The tag name does not appear in the checker definition
            * The attribute name does not appear in the checker definition
            * The attribute is not an attribute of the given tag
            * The value is not acceptable according to the checker definition
        """
        if tag not in self._checker.tokens():
            raise ValueError, "'%s' is not a valid element tag" % tag
        if att not in self._checker.tokens():
            raise ValueError, "'%s' is not a valid attribute name" % (att)

        tagcheck = self._checker.get(tag)
        if att not in tagcheck.attributes:
            raise ValueError, "Invalid attribute for %s: %s" % (tag, att)

        attcheck = self._checker.get(att)
        try:
            attcheck(value)
        except:
            raise ValueError, "Invalid value for %s: '%s'" % (att, value)


        elist = list(self._elem.findall('.//%s' % tag))
        if elist == [] and tag == self._elem.tag:
            elem = self._elem
        else:
            elem = elist[nth]
        elem.set(att, str(value))

    def _add_elem(self, tag_name, text, attrib=None):
        """_add_elem(tag_name, text, attrib=None)
        Adds a child element in the appropriate place in the tree.
        Raises an IndexError if the checker does not allow an addition child
        of tag_name.
        """
        if attrib is None:
            attrib = {}
        last_child = None
        count = 0
        for child in self._elem.findall('.//%s' % tag_name):
            count += 1
            last_child = child
        ch = self._checker.get(tag_name)
        if count >= ch.max_occurs:
            raise IndexError(
                "cannot add %s node. (max_occurs reached)" % tag_name )
        if last_child is None:
            new_child = ET.SubElement(self._elem, tag_name, attrib)
        else:
            new_child = ET.Element(tag_name, attrib)
            self._elem.insert(
                self._elem._children.index(last_child)+1,
                new_child)
        new_child.text = str(text)

        return new_child

    def _get_child_wrap(self, tag_name, nth=0):
        """_get_child_wrap(tag_name, nth=0)
        Returns a wrap object for the nth child node
        """

        ch = self._checker.get(tag_name)

        elist = list(self._elem.findall('.//%s' % tag_name))
        elem = elist[nth]

##        return self.__class__(ch, elem)
        return Wrap(ch, elem)

    ## new 0.4.7
    def __getattr__(self, prop):
        if prop in self._checker.tokens():
            nm, att = self._checker.path_to(prop)
            #~ print nm, att
            xpth = self._checker.xpath_to(prop)
            node = self._elem.find(xpth)
            ch = self._checker.get(prop)
            #~ print node, node.text
            if node is  None:
                return None
            if att:
                return node.get(prop)
            else:
                if ch.max_occurs > 1:
                    return [n.text for n in self._elem.findall(xpth)]
                else:
                    return node.text
            return None

        else:
            return self.__getattribute__(prop)

    ## new 0.4.7
    def tokens(self):
        "returns a list of checker tokens"
        return self._checker.tokens()



import unittest
from core import XCheck, XCheckError
from boolcheck import BoolCheck
from textcheck import TextCheck, EmailCheck
from numbercheck import IntCheck
from listcheck import SelectionCheck
from datetimecheck import DatetimeCheck
from loader import load_checker


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
        self.assertEqual(w0._get_elem_value('street'),
            '100 Main St', "sub element value misread")
        self.assertEqual(w1._get_elem_value('street'), '318 West Nowhere Ln')

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
    unittest.main(verbosity=1)



