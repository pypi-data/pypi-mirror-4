###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
Monkey-patch for zope.browserpage that adds log messages mentioning all
the page templates that were rendered during request handling.

Used automatically if you enable ``monkeypatch=True`` for LogviewMiddleware.
"""

import logging
import threading
import time


log = logging.getLogger('template')


def patchViewPageTemplateFile():
    """Monkey-patch ViewPageTemplateFile.__call__ to log template names."""
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
    if ViewPageTemplateFile.__call__.__name__ == 'call_pt':
        return # already patched
    orig_call = ViewPageTemplateFile.__call__
    indent = threading.local()
    def call_pt(self, instance, *args, **keywords):
        level = getattr(indent, 'level', 0)
        prefix = '- ' * level
        log.debug('%srendering %s', prefix, self.filename)
        indent.level = level + 1
        started = time.time()
        try:
            return orig_call(self, instance, *args, **keywords)
        finally:
            duration = time.time() - started
            indent.level = level
            log.debug('%srendered in %d ms', prefix, duration * 1000)
    call_pt.orig_call = ViewPageTemplateFile.__call__
    ViewPageTemplateFile.__call__ = call_pt


def unpatchViewPageTemplateFile():
    """Undo patchViewPageTemplateFile()."""
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
    if ViewPageTemplateFile.__call__.__name__ != 'call_pt':
        return # not patched
    orig_call = ViewPageTemplateFile.__call__.orig_call
    ViewPageTemplateFile.__call__ = orig_call

