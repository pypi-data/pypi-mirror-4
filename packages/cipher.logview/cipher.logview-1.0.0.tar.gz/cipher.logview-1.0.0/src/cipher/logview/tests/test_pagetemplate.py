###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import doctest
import unittest

from .. import testing
from ..pagetemplate import (patchViewPageTemplateFile,
                            unpatchViewPageTemplateFile,
                            log)

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    SKIP_TESTS = True
else:
    SKIP_TESTS = False


class ResponseStub(object):
    def getHeader(self, header):
        return None
    def setHeader(self, header, value):
        pass

class RequestStub(object):
    debug = False
    response = ResponseStub()

class ViewStub(object):
    context = None
    request = RequestStub()


def doctest_patchViewPageTemplateFile():
    r"""Test for patchViewPageTemplateFile

        >>> patchViewPageTemplateFile()
        >>> view = ViewStub()
        >>> pt = ViewPageTemplateFile('sample.pt').__get__(view, ViewStub)
        >>> nested = ViewPageTemplateFile('nested.pt').__get__(view, ViewStub)
        >>> print pt(nested=nested).strip() # doctest: +ELLIPSIS
        rendering .../cipher/logview/tests/sample.pt
        - rendering .../cipher/logview/tests/nested.pt
        - rendered in 0 ms
        rendered in 0 ms
        <p>Hello from sample.pt!</p>
        <p>Hello from nested.pt!</p>

    """


def doctest_unpatchViewPageTemplateFile():
    """Test for unpatchViewPageTemplateFile

        >>> orig_call = ViewPageTemplateFile.__call__

        >>> patchViewPageTemplateFile()
        >>> unpatchViewPageTemplateFile()

    Note: use == and not is, since it's an unbound method

        >>> ViewPageTemplateFile.__call__ == orig_call
        True

    What if we unpatch when it's not patched?

        >>> unpatchViewPageTemplateFile()
        >>> ViewPageTemplateFile.__call__ == orig_call
        True

    What if we patch twice then unpatch once?

        >>> patchViewPageTemplateFile()
        >>> patchViewPageTemplateFile()
        >>> unpatchViewPageTemplateFile()
        >>> ViewPageTemplateFile.__call__ == orig_call
        True

    """


def setUp(test):
    testing.setUpLogging(log)
    testing.setUpFrozenTime()
    test.orig_call = ViewPageTemplateFile.__call__


def tearDown(test):
    ViewPageTemplateFile.__call__ = test.orig_call
    testing.tearDownFrozenTime()
    testing.tearDownLogging(log)


def test_suite():
    if SKIP_TESTS:
        print
        print "Skipping some tests because zope.browserpage is not in sys.path"
        print
        return unittest.TestSuite()
    else:
        return doctest.DocTestSuite(setUp=setUp, tearDown=tearDown)
