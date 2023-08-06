"""
Define en passant helper objects.
"""

import sys
_PY3 = sys.version_info[0] > 2

class Passer(object):
    
    def __init__(self):
        self.value = None

    def _grab(self, other):
        """
        Get the value of the second operand, and return it as well.
        """
        self.value = other
        return other
        
    def _bool(self):
        """
        Return the boolean value of our value.
        """
        return bool(self.value)
    
    if _PY3:
        __truediv__ = _grab
        __bool__    = _bool
    else:
        __div__     = _grab
        __nonzero__ = _bool

    # define alterate operators (< and <=)
    __lt__ = _grab
    __le__ = _grab
    
    def __call__(self, *args):
        return self.value
    
    def __getattr__(self, name):
        try:
            return object.__getattr__(self, name)
        except AttributeError:
            return getattr(self.value, name)
    
        
    
    def __getitem__(self, n):
        return self.value.__getitem__(n)
    
    def __setitem__(self, n, value):
        return self.value.__setitem__(n, value)

    def __setattr__(self, name, value):
        if name == 'value':
            object.__setattr__(self, name, value)
        else:
            setattr(self.value, name, value)
