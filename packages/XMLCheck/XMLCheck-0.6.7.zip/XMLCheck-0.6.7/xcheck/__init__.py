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
__version__ = '0.6.7'



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