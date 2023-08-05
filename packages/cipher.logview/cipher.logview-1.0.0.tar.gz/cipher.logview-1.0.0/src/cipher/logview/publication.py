###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
Monkey-patch ZopePublication to add logging of the view class name.
"""

import inspect
import logging

try:
    from zope.security.proxy import removeSecurityProxy
except ImportError:
    def removeSecurityProxy(obj):
        return obj

try:
    from zope.interface.declarations import providedBy
except ImportError:
    def providedBy(obj):
        return []


log = logging.getLogger('publication')


def getClassOf(view):
    """Return the class of a view object."""
    cls = removeSecurityProxy(view).__class__
    # pagelet zcml registrations construct synthetic subclasses
    # there should probably be a similar check for regular browser pages
    if cls.__module__ == 'z3c.pagelet.zcml':
        cls = cls.__bases__[0]
    return cls


def getNameOf(view):
    """Return the full name of the view class."""
    cls = getClassOf(view)
    return cls.__module__ + '.' + cls.__name__


def getSourceOf(view):
    """Return the source filename and line number range for the view class."""
    cls = getClassOf(view)
    try:
        filename = inspect.getsourcefile(cls)
    except TypeError:
        filename = None
    if not filename:
        return 'no source information available'
    try:
        lines, firstlineno = inspect.getsourcelines(cls)
        lastlineno = firstlineno + len(lines) - 1
    except IOError:
        return filename
    else:
        return '%s (lines %d-%d)' % (filename, firstlineno, lastlineno)


UNKNOWN = object()


def getContext(view, default=UNKNOWN):
    """Return the context of a view."""
    return getattr(removeSecurityProxy(view), 'context', UNKNOWN)


def getProvidedBy(obj):
    """Return a string describing the interfaces provided by an object."""
    ifaces = providedBy(obj)
    return ', '.join(iface.__name__ for iface in ifaces) or 'nothing'


def patchZopePublication():
    """Monkey-patch ZopePublication.callObject to log view class."""
    from zope.app.publication.zopepublication import ZopePublication
    if ZopePublication.callObject.__name__ == 'callObject_patched':
        return # already patched
    orig_callObject = ZopePublication.callObject
    def callObject_patched(self, request, obj):
        log.debug('Calling %s - %s', getNameOf(obj), getSourceOf(obj))
        context = getContext(obj)
        if context is not UNKNOWN:
            log.debug('View context is %s, providing %s',
                      repr(context), getProvidedBy(context))
        return orig_callObject(self, request, obj)
    callObject_patched.orig_callObject = orig_callObject
    ZopePublication.callObject = callObject_patched


def unpatchZopePublication():
    """Undo patchZopePublication()."""
    from zope.app.publication.zopepublication import ZopePublication
    if ZopePublication.callObject.__name__ != 'callObject_patched':
        return # not patched
    orig_callObject = ZopePublication.callObject.orig_callObject
    ZopePublication.callObject = orig_callObject

