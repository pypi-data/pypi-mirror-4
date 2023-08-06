###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import doctest
import sys

from ..stackformatter import format_stack, extract_stack
from ..stackformatter import format_tb, extract_tb


def a(*args, **kw):
    __traceback_info__ = 'hello from a'
    b(*args, **kw)

def b(*args, **kw):
    __traceback_info__ = ('hello', 'from', 'b')
    c(*args, **kw)

def c(*args, **kw):
    __traceback_supplement__ = VeryExplosiveTBS, 'arg'
    print(''.join(format_stack(*args, **kw)).rstrip())

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
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in a
          b(*args, **kw)
         - __traceback_info__: hello from a
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in b
          c(*args, **kw)
         - __traceback_info__: ('hello', 'from', 'b')
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in c
          print(''.join(format_stack(*args, **kw)).rstrip())

    """


def doctest_format_stack_safe_against_buggy_repr():
    """Test format_stack

      >>> explode(limit=2) # doctest: +REPORT_NDIFF,+ELLIPSIS
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in explode
          c(*args, **kw)
         - __traceback_info__: <unrepresentable: Exception('some __repr__s are buggy',)>
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in c
          print(''.join(format_stack(*args, **kw)).rstrip())

    """


def doctest_format_stack_safe_against_buggy_exception_repr():
    """Test format_stack

      >>> explode_with_nested_explosive(limit=2) # doctest: +REPORT_NDIFF,+ELLIPSIS
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in explode_with_nested_explosive
          c(*args, **kw)
         - __traceback_info__: <unrepresentable>
        File ".../cipher/logview/tests/test_stackformatter.py", line ..., in c
          print(''.join(format_stack(*args, **kw)).rstrip())

    """


def doctest_extract_stack():
    """Test for extract_stack

        >>> extract_stack(traceback_supplement=True) # doctest: +ELLIPSIS
        [...]

    """


class TBS(object):
    source_url = 'www.example.com'
    line = 11
    column = 42
    expression = '2 + 2'
    warnings = ['be cool', 'stay at school']
    def __init__(self, *args):
        self.args = args
    def getInfo(self):
        return ('I ran out\nof creative ideas\nfor this test\nalso args: %s'
                % repr(self.args))


class ExplosiveTBS(object):
    def __init__(self, *args):
        raise Exception('some __init__s are buggy')


class VeryExplosiveTBS(object):
    def __init__(self, *args):
        raise ExplosiveException()


def doctest_format_tb():
    """Test for format_tb

        >>> try:
        ...     __traceback_supplement__ = TBS, 'arg'
        ...     raise Exception
        ... except Exception:
        ...     print(''.join(format_tb(sys.exc_info()[2])).rstrip())
        ...     # doctest: +ELLIPSIS
          File "<doctest cipher.logview.tests.test_stackformatter.doctest_format_tb[0]>", line 3, in <module>
            raise Exception
           - __traceback_supplement__:
             - source_url: www.example.com
             - line: 11
             - column: 42
             - expression: 2 + 2
             - warning: be cool
             - warning: stay at school
             - getInfo():
               I ran out
               of creative ideas
               for this test
               also args: ('arg',)

    """


def doctest_format_tb_explosive():
    """Test for format_tb

        >>> try:
        ...     __traceback_supplement__ = ExplosiveTBS, 'arg'
        ...     raise Exception
        ... except Exception:
        ...     print(''.join(format_tb(sys.exc_info()[2])).rstrip())
        ...     # doctest: +ELLIPSIS
          File "<doctest cipher.logview.tests.test_stackformatter.doctest_format_tb_explosive[0]>", line 3, in <module>
            raise Exception
           - __traceback_supplement__:
             - <unrepresentable: Exception('some __init__s are buggy',)>

    """


def doctest_format_tb_very_explosive():
    """Test for format_tb

        >>> try:
        ...     __traceback_supplement__ = VeryExplosiveTBS, 'arg'
        ...     raise Exception
        ... except Exception:
        ...     print(''.join(format_tb(sys.exc_info()[2])).rstrip())
        ...     # doctest: +ELLIPSIS
          File "<doctest cipher.logview.tests.test_stackformatter.doctest_format_tb_very_explosive[0]>", line 3, in <module>
            raise Exception
           - __traceback_supplement__:
             - <unrepresentable>

    """


def doctest_extract_tb():
    """Test for extract_stack

        >>> try:
        ...     raise Exception
        ... except Exception:
        ...     extract_tb(sys.exc_info()[2], traceback_supplement=False)
        ...     # doctest: +ELLIPSIS
        [...]

    """


def test_suite():
    return doctest.DocTestSuite()

