from utils import get_elem

class Wrap(object):
    """Wrap(checker, element)
    Creates a object Wrapper around an element that must validate to the
    checker object.

    Arguments:
    :param checker: an XCheck instance. Should not be an instance of a sub-class
    :type checker: XCheck
    :param element: An ElementTree:Element or string representation of an
    ElementTree.Element
    :type element
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
        Raises a ValueError if any of the following are true:
            The tag name does not appear in the checker definition
            The attribute name does not appear in the checker definition
            The attribute is not an attribute of the given tag
            The value is not acceptable according to the checker definition
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

if __name__=='__main__':
    from numbercheck import IntCheck
    i = IntCheck('value', min=1, max=6)
    print i
    print i(2)

    e = get_elem('<value>2</value>')
    w = Wrap(i, e)
    print w
