"""dictwrap
Two tools for turning an XML node into a dictionary and back.
"""
from elementtree import ElementTree as ET

from core import XCheck
from boolcheck import BoolCheck
from numbercheck import IntCheck
from listcheck import ListCheck, SelectionCheck
from textcheck import TextCheck, EmailCheck


__all__ = ['node_to_dict', 'dict_to_node']

def node_to_dict(node, checker):
    "creates a dictionary represinting a node, using a checker as a guide"
    res = {}

    for key in checker.attributes.keys():

        attch = checker.get(key)
        val = node.get(key)

        if val is not None:
            val = attch(val, normalize=True)
            res["%s.%s" % (checker.name, key)] = val

    if checker.children:
        for child in checker.children:
            child_node = node.find(child.name)
            child_check = checker.get(child.name)

            if child_check.max_occurs > 1:

                res[child_check.name] = []
                child_nodes = node.findall(child.name)
                for node in child_nodes:
                    res[child_check.name].append(node_to_dict( \
                        node, child_check))
            else:
                if child_node is not None:
                    if child.children:
                        res[child.name] = node_to_dict(child_node, child_check)
                    else:
                        res.update(node_to_dict(child_node, child_check))
    else:
        text = node.text
        res[checker.name] = checker(text, normalize=True)
    return res

AS_STRING_CLASSES = (BoolCheck, ListCheck, IntCheck)

def dict_to_node(input_dict, checker):
    """Creates an ElementTree.Element based on the dictionary.
    dict_to_node does not check the validity of the node.
    Always call the checker with the created node to assure it is valid
    """
    elem = ET.Element(checker.name)
    for att in checker.attributes.keys():
        try:
            val = input_dict.pop("%s.%s" % (checker.name, att))
        except KeyError:
            val = None
        if val is not None:
            att_check = checker.get(att)
            if isinstance(att_check, AS_STRING_CLASSES):
                val = att_check(val, as_string=True)
            else:
                val = str(val)
            elem.set(att, val)
    if checker.children:

        for child in checker.children:

            if child.max_occurs == 1:
                if child.children:
                    sub_d = input_dict.pop(child.name, None)
                    if sub_d:
                        sub_elem = dict_to_node(sub_d, child)
                        elem.append(sub_elem)
                else:
                    newd = {}
                    for key in input_dict:
                        if key.startswith(child.name):
                            newd[key] = input_dict[key]
                    if newd:
                        sub_elem = dict_to_node(newd, child)
                        elem.append(sub_elem)
                        for key in newd:
                            input_dict.pop(key)
            else:
                for sub_d in input_dict.pop(child.name):
                    sub_elem = dict_to_node(sub_d, child)
                    elem.append(sub_elem)
    else:
        val = input_dict.pop(checker.name)
        if isinstance(checker, AS_STRING_CLASSES):
            elem.text = checker(val, as_string=True)
        else:
            elem.text = checker(val, normalize=True)

    return elem


def local_test():
    "sample usage and simple test"
    nick = BoolCheck('nick', required=False)
    first_name = TextCheck('first', min_length = 1)
    first_name.addattribute(nick)

    last_name = TextCheck('last', min_length = 1)
    code = IntCheck('code', minOccurs=1, max_occurs=5)
    code.addattribute(TextCheck('word', required=False) )
    name = XCheck('name', children=[first_name, last_name, code])

    emailtype = SelectionCheck('type', values = ['home', 'work', 'personal'])
    email = EmailCheck('email', max_occurs=2)
    email.addattribute(emailtype)
    street = TextCheck('street')
    city = TextCheck('city')

    address = XCheck('address', children = [street, city, email],
         max_occurs = 4)

    dude = XCheck('dude', children=[name, address],
        help="A simple contact list item")

    dude_node = ET.fromstring("""<dude id="1">
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
    from pprint import pprint
    pprint( node_to_dict(dude_node, dude) )

if __name__ == '__main__':
    local_test()