class InfinityPlus:
    """InfinityPlus()
    Simple number-like class that assumes anything you compare it to is
    smaller than itself.
    """
    def __init__(self): pass
    def __lt__(self,num): return False
    def __gt__(self,num): return True
    def __le__(self,num): return False
    def __ge__(self,num): return True
    def __eq__(self,num):
        return num.__class__ == self.__class__
    def __ne__(self,num):
        return not self.__eq__(num)
    def __repr__(self): return "InfinityPlus"
    def __int__(self): raise ValueError, "Infinity cannot be converted to integer"
    def __float__(self): raise ValueError, "Infinity cannot be converted to float"
    def __add__(self, other): return self
    def __sub__(self, other): return self
    def __mul__(self, other): return self
    def __div__(self, other): return self
    def __radd__(self, other): return self

class InfinityMinus:
    """InfinityMinus()
    Simple number-like class that assumes anything you compare it to is
    larger than itself.
    """
    def __init__(self): pass
    def __int__(self): return self
    def __lt__(self,num): return True
    def __gt__(self,num): return False
    def __le__(self,num): return True
    def __ge__(self,num): return False
    def __eq__(self,num):
        if num.__class__ == self.__class__: return True
        else: return False
    def __ne__(self,num):
        return not self.__eq__(num)
    def __repr__(self): return "InfinityMinus"

INF = InfinityPlus()
NINF = InfinityMinus()

