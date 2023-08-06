from xcheck import XCheck, XCheckError
from textcheck import TextCheck, EmailCheck, URLCheck
from boolcheck import BoolCheck
from listcheck import NoSelectionError, BadSelectionsError
from listcheck import SelectionCheck, ListCheck
from numbercheck import IntCheck, DecimalCheck
from datetimecheck import DatetimeCheck
from utils import get_elem

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

if __name__=='__main__':
    from elementtree import ElementTree as ET
    txt = """<text name='person'>
    <attributes><int name='id'/></attributes>
    </text>"""
    ch = load_checker(txt)
    print ch
    print ch.attributes, bool(ch.attributes)
    print ch.name

    ET.dump( ch.to_definition_node() )
