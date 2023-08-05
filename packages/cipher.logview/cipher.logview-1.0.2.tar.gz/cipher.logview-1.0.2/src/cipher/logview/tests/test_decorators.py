###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import doctest

from .. import testing
from ..decorators import name_of, timed, log


def simple_fn():
    pass


class SomeClass(object):
    def a_method(self):
        pass


def doctest_name_of():
    """Test for name_of

        >>> name_of(simple_fn)
        'simple_fn'

        >>> name_of(SomeClass.a_method, (SomeClass(),))
        'SomeClass.a_method'

    """


@timed
def outer_fn(a, b):
    inner_fn(a + b)


@timed
def inner_fn(c):
    print c


def doctest_timed():
    """Test for timed

        >>> outer_fn(1, 2)
        outer_fn entered
        - inner_fn entered
        3
        - inner_fn: 0 ms
        outer_fn: 0 ms

    """


def setUp(test):
    testing.setUpLogging(log)
    testing.setUpFrozenTime()


def tearDown(test):
    testing.tearDownFrozenTime()
    testing.tearDownLogging(log)


def test_suite():
    return doctest.DocTestSuite(setUp=setUp, tearDown=tearDown)
