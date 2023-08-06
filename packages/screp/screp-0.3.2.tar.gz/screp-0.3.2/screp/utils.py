import sys

from cssselect import GenericTranslator


def raise_again(s):
    """
    Raises an exception with message msg using the class and traceback from sys.exc_info.
    """
    (t, v, tb) = sys.exc_info()
    assert t is not None
    raise t(s), None, tb


def preprocess_selector(selector):
    # no selector means universal selector
    if selector == '':
        return '*'
    else:
        return selector


generic_translator = GenericTranslator()
