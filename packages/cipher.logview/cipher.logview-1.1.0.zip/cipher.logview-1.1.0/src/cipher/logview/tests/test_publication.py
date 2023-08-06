###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import doctest
import unittest

from .. import testing
from ..publication import (
    patchZopePublication, unpatchZopePublication, log,
    getClassOf, getNameOf, getSourceOf, getContext)

try:
    from zope.app.publication.zopepublication import ZopePublication
except ImportError:
    SKIP_TESTS = True
else:
    SKIP_TESTS = False


class ViewStub(object):
    context = None
    def __call__(self):
        return 'hi'

class RequestStub(object):
    def getPositionalArguments(self):
        return ()
    def get(self, name):
        return None # pragma: nocover


def doctest_getClassOf_method():
    """Test for getClassOf

        >>> getClassOf(ViewStub().__call__) is ViewStub
        True

    """


def doctest_getClassOf_syntetic_pagelet_class():
    """Test for getClassOf

        >>> view_class = type('dynamic subclass', (ViewStub, ),
        ...                   {'__module__': 'z3c.pagelet.zcml'})
        >>> getClassOf(view_class()) is ViewStub
        True

    """


def doctest_getNameOf_method():
    """Test for getNameOf

        >>> getNameOf(ViewStub().__call__)
        'cipher.logview.tests.test_publication.ViewStub.__call__'

    """


def doctest_getSourceOf_no_source():
    """Test for getSourceOf

    Python builtins are handy things that don't have source information

        >>> getSourceOf(str)
        'no source information available'

    """


def doctest_getContext_method():
    """Test for getContext_method

        >>> view = ViewStub()
        >>> view.context = object()
        >>> getContext(view.__call__) is view.context
        True

    """


def doctest_patchZopePublication():
    """Test for patchZopePublication

        >>> patchZopePublication()

        >>> pub = ZopePublication(None)
        >>> view = ViewStub()
        >>> pub.callObject(RequestStub(), view) # doctest: +ELLIPSIS
        Calling cipher.logview.tests.test_publication.ViewStub - .../cipher/logview/tests/test_publication.py (lines ...)
        View context is None, providing nothing
        'hi'

    """


def doctest_unpatchZopePublication():
    """Test for unpatchZopePublication

        >>> orig_callObject = ZopePublication.callObject

        >>> patchZopePublication()
        >>> unpatchZopePublication()

    Note: use == and not is, since it's an unbound method

        >>> ZopePublication.callObject == orig_callObject
        True

    What if we unpatch when it's not patched?

        >>> unpatchZopePublication()
        >>> ZopePublication.callObject == orig_callObject
        True

    What if we patch twice then unpatch once?

        >>> patchZopePublication()
        >>> patchZopePublication()
        >>> unpatchZopePublication()
        >>> ZopePublication.callObject == orig_callObject
        True

    """


def setUp(test):
    testing.setUpLogging(log)
    test.orig_callObject = ZopePublication.callObject


def tearDown(test):
    ZopePublication.callObject = test.orig_callObject
    testing.tearDownLogging(log)


def test_suite():
    if SKIP_TESTS:
        print("")
        print("Skipping some tests because zope.app.publication is not in sys.path")
        print("")
        return unittest.TestSuite()
    else:
        return doctest.DocTestSuite(setUp=setUp, tearDown=tearDown)
