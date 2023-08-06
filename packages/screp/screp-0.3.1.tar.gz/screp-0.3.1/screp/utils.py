import sys


def raise_again(s):
    """
    Raises an exception with message msg using the class and traceback from sys.exc_info.
    """
    (t, v, tb) = sys.exc_info()
    assert t is not None
    raise t(s), None, tb
