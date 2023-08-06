"""XCheck
XMLChecker objects that can validate text, xml-formatted text,
or an elementtree.ElementTree node. XCheck objects can also
return checked data in a normalized form (BoolCheck, for example,
returns Boolean values, IntCheck returns an integer)

How to use:
1. Derive Checkers from XCheck
2. Customize the check_content function
3. Customize the normalizeValue function if necessary

"""
__version__ = '0.6.5'

__history__ = """
0.2 -- added XCheck.ToElem() and XCheck.toClass() methods
0.3 -- added XCheck.ToObject() method
0.4 -- added URLCheck class
0.4.1 (3.18.2010) -- Added as_string argument to DateTimeCheck.__call__
0.4.2 (3.20.2010) -- Added _rename method to XCheck
    Added tokens and tagnames methods to XCheck
    Updated XCheck.get to search all children
0.4.2.1 (7.21.2010) -- IntCheck normalizes to an integer
0.4.3 (8.22.2010) -- Added the Wrap class and tests
0.4.4 (9.1.2010) -- Fixed bug in text checker
0.4.4a (9.2.2010) -- Fixed bug in DateTimeCheck.dummy_value, added DummyValueTC
0.4.4b (9.4.2010) -- Clarified error message in SelectionCheck.check_content
0.4.5 (9.24.2010) -- Added XCheck.path_to method
0.4.6 (10.31.2010) -- Fixed Xcheck.path_to method
0.4.7 (11.5.2010) -- Added ability for Wrap to return node attributes
0.4.8 (12.12.2010) -- Added helpstring to XCheck, and helper methods
0.4.9 (12.17.2010) -- Added ListCtrl(_asList) keyword __call__
0.5.0 (12.19.2010) -- Added to_dict and from_dict methods
            -- changed ListCheck.__call__ _asList keyword to as_string
            -- ListCheck accepts lists of strings now
            -- added as_string keyword to BoolCheck.__call__
            -- added as_string keyword to IntCheck.__call__
            -- added dict_key method to XCheck for ease of use
            -- fixed bug in Wrap._get_child_Wrap
            -- changed Wrap to accept no element, creating a dummy if necessary
0.5.1 (07.04.2011) -- Fixed bug where DateTimeCheck.allow_none = True failed
0.5.2 (05.11.2012) -- Changed xcheck.attributes to be an ordered dict
0.5.3 (05.19.2012) -- added XCheck.insert_node
0.6.0 (01.01.2013) -- Edits for PEP 8
0.6.5 (01.24.2013) -- Updated load_checker, replaced _verbose with logging
      (03.09.2013) -- Added get_elem into the Wrap, so a string object can be
                      used as well
            -- Fixed Wrap._set_elem_value to add an element if needed
0.6.6 (04.15.2013) -- renamed xcheck submodule core
            -- Fixed bug 4 -- IntCheck was using _normalize instead of normalize
              as keyword argument
"""

from core import *
from textcheck import TextCheck, EmailCheck, URLCheck
from boolcheck import BoolCheck
from listcheck import NoSelectionError, BadSelectionsError
from listcheck import SelectionCheck, ListCheck
from numbercheck import IntCheck, DecimalCheck
from datetimecheck import DatetimeCheck
from wrap import Wrap
from loader import load_checker

from infinity import INF, NINF

if __name__=='__main__':
    print dir()