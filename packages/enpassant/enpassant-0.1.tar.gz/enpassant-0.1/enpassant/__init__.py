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