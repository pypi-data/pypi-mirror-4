XCheck
XMLChecker objects that can validate text, xml-formatted text,
or an elementtree.ElementTree node. XCheck objects can also
return checked data in a normalized form (BoolCheck, for example,
returns Boolean values, IntCheck returns an integer)

How to use:
1. Derive Checkers from XCheck
2. Customize the check_content function
3. Customize the normalizeValue function if necessary
