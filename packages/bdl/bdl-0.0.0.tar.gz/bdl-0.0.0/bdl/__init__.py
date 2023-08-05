from functools import wraps

def _live():
    try:
        import settings
        return not settings.NO_BDL
    except ImportError:
        return True
    except AttributeError:
        return True 


def typeify(obj):
    if isinstance(obj, type):
        return obj
    return type(obj)


class ReturnCheck:
    def __init__(self, expected_type):
        if not isinstance(expected_type, type):
            expected_type = type(expected_type)
        self.expected_type = expected_type
    
    def __call__(self, retval):
        if type(retval) != self.expected_type:
            raise TypeError("Expected a return value of %r, returned a %r instead" % (self.expected_type, type(retval)))
        return retval
    
def returns(retval):
    """returns is a dectorator to enforce return values
    >>> from bdl import returns
    >>> @returns(int)
    ... def a():
    ...     return 1
    ... 
    >>> a()
    1
    >>> @returns(str)
    ... def b():
    ...     return 1
    ... 
    >>> b()
    TypeError: Expected a return value of <type 'str'>, returned a <type 'int'> instead
"""
    
    def returns_dectorator(f):
        if not _live():
            return f
        @wraps(f)
        def check_return_value(*args, **kwargs):
            return ReturnCheck(retval)(f(*args, **kwargs))
        return check_return_value
    return returns_dectorator
            
