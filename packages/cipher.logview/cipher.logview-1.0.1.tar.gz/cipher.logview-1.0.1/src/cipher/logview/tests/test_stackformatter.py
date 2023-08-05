###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import doctest

from ..stackformatter import format_stack, extract_stack


def a(*args, **kw):
    __traceback_info__ = 'hello from a'
    b(*args, **kw)

def b(*args, **kw):
    __traceback_info__ = ('hello', 'from', 'b')
    c(*args, **kw)

def c(*args, **kw):
    print ''.join(format_stack(*args, **kw)).rstrip()

class Explosive(object):
    def __repr__(self):
        raise Exception('some __repr__s are buggy')

def explode(*args, **kw):
    __traceback_info__ = Explosive()
    c(*args, **kw)

class ExplosiveException(Exception):
    def __repr__(self):
        raise Exception('some __repr__s are buggy')

class ExtremelyExplosive(object):
    def __repr__(self):
        raise ExplosiveException()

def explode_with_nested_explosive(*args, **kw):
    __traceback_info__ = ExtremelyExplosive()
    c(*args, **kw)


def doctest_format_stack():
    """Test format_stack

      >>> a(limit=4) # doctest: +REPORT_NDIFF,+ELLIPSIS
        File "<doctest cipher.logview.tests.test_stackformatter.doctest_format_stack[0]>", line 1, in <module>
          a(limit=4) # doctest: +REPORT_NDIFF,+ELLIPSIS
        File ".../cipher/logview/tests/test_stackformatter.py", line 14, in a
          b(*args, **kw)
         - __traceback_info__: hello from a
        File ".../cipher/logview/tests/test_stackformatter.py", line 18, in b
          c(*args, **kw)
         - __traceback_info__: ('hello', 'from', 'b')
        File ".../cipher/logview/tests/test_stackformatter.py", line 21, in c
          print ''.join(format_stack(*args, **kw)).rstrip()

    """


def doctest_format_stack_safe_against_buggy_repr():
    """Test format_stack

      >>> explode(limit=2) # doctest: +REPORT_NDIFF,+ELLIPSIS
        File ".../src/cipher/logview/tests/test_stackformatter.py", line 29, in explode
          c(*args, **kw)
         - __traceback_info__: <unrepresentable: Exception('some __repr__s are buggy',)>
        File ".../src/cipher/logview/tests/test_stackformatter.py", line 21, in c
          print ''.join(format_stack(*args, **kw)).rstrip()

    """


def doctest_format_stack_safe_against_buggy_exception_repr():
    """Test format_stack

      >>> explode_with_nested_explosive(limit=2) # doctest: +REPORT_NDIFF,+ELLIPSIS
        File ".../src/cipher/logview/tests/test_stackformatter.py", line 41, in explode_with_nested_explosive
          c(*args, **kw)
         - __traceback_info__: <unrepresentable>
        File ".../src/cipher/logview/tests/test_stackformatter.py", line 21, in c
          print ''.join(format_stack(*args, **kw)).rstrip()

    """


def doctest_extract_stack():
    """Test for extract_stack

        >>> extract_stack() # doctest: +ELLIPSIS
        [...]

    """


def test_suite():
    return doctest.DocTestSuite()

