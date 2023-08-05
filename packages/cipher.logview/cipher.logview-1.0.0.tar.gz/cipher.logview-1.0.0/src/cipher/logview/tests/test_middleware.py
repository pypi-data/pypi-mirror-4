###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import doctest
import logging
import re

from ..middleware import LogviewMiddleware, TimeBar, logview_filter_factory
from .. import stackformatter, pagetemplate, publication


def LogRecord(msg, args=(), name='timeline', level=logging.DEBUG,
              exc_info=None, pathname=None, lineno=None):
    return logging.LogRecord(name=name, level=level, msg=msg, args=args,
                             exc_info=exc_info, pathname=pathname,
                             lineno=lineno)


class TemplateStub(object):

    def __init__(self, name='untitled'):
        self.name = name

    def render(self, **vars):
        return (
            '<head><title>{name}</title></head>\n'
            '<body>\n'
            '  <table class="lalala">\n'
            '  </table>\n'
            '</body>\n').format(name=self.name)


def doctest_LogviewMiddleware_defaults():
    """Test for LogviewMiddleware

        >>> mw = LogviewMiddleware(None, {})
        >>> mw.stack_formatter
        'cipher.logview.format_stack'
        >>> mw.reqhandler.stack_formatter is stackformatter.format_stack
        True

    """


def fake_template_patch():
    print "Monkey-patching ViewPageTemplate.__call__"

def fake_publication_patch():
    print "Monkey-patching ZopePublication.callObject"


def failing_patch():
    raise ImportError('fake import error')


def doctest_LogviewMiddleware_monkeypatch():
    """Test for LogviewMiddleware

        >>> orig_template_patch = pagetemplate.patchViewPageTemplateFile
        >>> orig_publication_patch = publication.patchZopePublication
        >>> pagetemplate.patchViewPageTemplateFile = fake_template_patch
        >>> publication.patchZopePublication = fake_publication_patch

        >>> mw = LogviewMiddleware(None, {}, monkeypatch=True)
        Monkey-patching ViewPageTemplate.__call__
        Monkey-patching ZopePublication.callObject

    This doesn't fail if there's no ViewPageTemplate to monkey-patch

        >>> pagetemplate.patchViewPageTemplateFile = failing_patch
        >>> publication.patchZopePublication = failing_patch

        >>> mw = LogviewMiddleware(None, {}, monkeypatch=True)

        >>> pagetemplate.patchViewPageTemplateFile = orig_template_patch
        >>> publication.patchZopePublication = orig_publication_patch

    """


def doctest_LogviewMiddleware_render_no_timing_messages():
    """Test for LogviewMiddleware.render

        >>> mw = LogviewMiddleware(None, {})
        >>> mw.mako.get_template = TemplateStub
        >>> mw.render_extra_stuff = lambda *args, **kw: ''
        >>> html = mw.render('logbar.mako')
        >>> print html,
        <head><title>logbar.mako</title></head>
        <body>
          <table class="lalala">
          </table>
        </body>

    """


def doctest_LogviewMiddleware_render_with_timing_messages():
    r"""Test for LogviewMiddleware.render

        >>> mw = LogviewMiddleware(None, {})
        >>> mw.mako.get_template = TemplateStub
        >>> mw.render_extra_stuff = lambda *args, **kw: '<extra stuff>\n  '
        >>> html = mw.render('logbar.mako')
        >>> print html,
        <head><title>logbar.mako</title></head>
        <body>
          <extra stuff>
          <table class="lalala">
          </table>
        </body>

    """


def doctest_LogviewMiddleware_render_extra_stuff_no_time_bars():
    """Test for LogviewMiddleware.render_extra_stuff

        >>> mw = LogviewMiddleware(None, {})
        >>> events = [
        ...     LogRecord('Testing...'),
        ... ]
        >>> mw.render_extra_stuff('nobodycares', events=events, start=0,
        ...                       tottime=0.2)
        ''

    """


def doctest_LogviewMiddleware_render_extra_stuff_time_bars():
    """Test for LogviewMiddleware.render_extra_stuff

        >>> mw = LogviewMiddleware(None, {})
        >>> events = [
        ...     LogRecord('- somefunc entered'),
        ...     LogRecord('- somefunc: 102 ms'),
        ... ]
        >>> html = mw.render_extra_stuff('nobodycares', events=events, start=0,
        ...                              tottime=0.2)
        >>> html != ''
        True
        >>> 'somefunc' in html or html
        True

    """


def doctest_TimeBar_render_scales_down():
    """Test for TimeBar.render

        >>> bar = TimeBar(0, 20.0) # 20 seconds
        >>> html = bar.render()

    We're keeping the width less than 1000px by increasing the scaling factor

        >>> re.findall('width: [0-9]+px', html)
        ['width: 612px']

    That number is 20 (seconds) * 500 px / 2**4, minus some padding.

    We put second marks at least 10px from each other, which means we
    omit the minor 100ms marks but keep the ones for every second

        >>> list(bar.get_marks()) # doctest: +NORMALIZE_WHITESPACE
        [(31, True), (62, True), (93, True), (124, True), (155, True),
         (186, True), (217, True), (248, True), (279, True), (310, True),
         (341, True), (372, True), (403, True), (434, True), (465, True),
         (496, True), (527, True), (558, True), (589, True), (620, True)]

    """


def doctest_TimeBar_render_distributes_error():
    """Test for TimeBar.render

        >>> bar = TimeBar(0, 1.0) # 1 second

        >>> bar.enter(0, 'foo')
        >>> bar.leave(1.0/3, 'foo')

        >>> bar.enter(1.0/3, 'bar')
        >>> bar.leave(2.0/3, 'bar')

        >>> bar.enter(2.0/3, 'baz')
        >>> bar.leave(1.0, 'baz')

        >>> html = bar.render()

    We expect the three bars to add up to an even 500px (minus padding), even
    though 500 doesn't divide by 3 exactly

        >>> widths = re.findall(' width: ([0-9]+)px', html)
        >>> borders = re.findall('border-width: 1px ([0-9]+)px', html)
        >>> paddings = re.findall('padding: 3px ([0-9]+)px', html)
        >>> sum(map(int, widths + 2*borders + 2*paddings))
        500

    """


def doctest_logview_filter_factory():
    """Test for logview_filter_factory

        >>> app = object()
        >>> filter = logview_filter_factory({})
        >>> wrapped_app = filter(app)
        >>> isinstance(wrapped_app, LogviewMiddleware)
        True
        >>> wrapped_app.app is app
        True

    """


def test_suite():
    return doctest.DocTestSuite()
