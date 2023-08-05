###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
WSGI middleware that adds a JavaScripty log bar that shows all the log
messages produced while handling a request.
"""

import gc
import re
import sys

import dozer
from paste.util.converters import asbool

from . import decorators, pagetemplate, publication


class LogviewMiddleware(dozer.Logview):



    def __init__(self, app, config=None, **kwargs):
        # override some defaults
        if not config or 'stack_formatter' not in config:
            kwargs.setdefault('stack_formatter', 'cipher.logview.format_stack')
        if asbool(kwargs.get('monkeypatch', False)):
            try:
                pagetemplate.patchViewPageTemplateFile()
            except ImportError:
                pass
            try:
                publication.patchZopePublication()
            except ImportError:
                pass
        super(LogviewMiddleware, self).__init__(app, config, **kwargs)

    def render(self, name, **vars):
        gc.collect()
        html = super(LogviewMiddleware, self).render(name, **vars)
        extra = self.render_extra_stuff(name, **vars)
        if not extra:
            return html
        parts = html.partition('<table')
        return ''.join(parts[:1] + (extra,) + parts[1:])

    def extract_timeline(self, events, start, tottime):
        logger_name = decorators.log.name
        enter_rx = re.compile('^((?:- )*)([a-zA-Z0-9_.]+) entered$')
        leave_rx = re.compile('^((?:- )*)([a-zA-Z0-9_.]+): (\d+) ms$')
        timebars = []
        for event in events:
            if event.name == logger_name:
                msg = event.getMessage()
                m = enter_rx.match(msg)
                if m:
                    level = len(m.group(1)) / 2
                    while level >= len(timebars):
                        timebars.append(TimeBar(start, tottime))
                    timebars[level].enter(event.created, m.group(2))
                    continue
                m = leave_rx.match(msg)
                if m:
                    level = len(m.group(1)) / 2
                    timebars[level].leave(event.created, m.group(2))
        return timebars

    def render_extra_stuff(self, name, events, start, tottime, **vars):
        timebars = self.extract_timeline(events, start, tottime)
        if not timebars:
            return ''
        html = [
            '<div style="background: #ddd; margin: 0; padding: 6px;'
                       ' width: 100%; overflow: auto;">\n'
            '<div style="display: inline-block; overflow: hidden;'
                       ' position: relative;'
                       ' background: #444; padding: 4px;">',
        ]
        for pos, major in timebars[0].get_marks():
            html.append('<span style="position: absolute;'
                                    ' top: %(vpos)dpx; bottom: %(vpos)dpx;'
                                    ' left: %(pos)dpx; width: 0px;'
                                    ' border-left: 1px %(style)s %(color)s;"></span>'
                        % dict(pos=pos,
                               vpos=1 if major else 4,
                               style='solid' if major else 'dotted',
                               color='#888' if major else '#555'))
        for n, timebar in enumerate(timebars):
            if n > 0:
                html.append('<div style="height: 2px"></div>\n')
            html.append(timebar.render())
        html.append('</div>\n</div>\n')
        return ''.join(html)


def best_contrast(color):
    return 'black' if color in ('yellow', 'cyan', 'orange') else 'white'


class TimeBar(object):

    COLORS = ('blue', 'green', 'yellow', 'cyan', 'orange', 'purple')

    def __init__(self, start_timestamp, tottime):
        self.parts = []
        self.start_timestamp = self.last_ts = start_timestamp
        self.tottime = tottime
        self.closed = False

    def enter(self, timestamp, fn):
        # NB: never nest enter() calls, we don't handle that at this level
        if self.last_ts != None:
            delta = timestamp - self.last_ts
            if delta > 0:
                self.parts.append(('', delta))
        self.last_ts = timestamp

    def leave(self, timestamp, fn):
        delta = timestamp - self.last_ts
        self.parts.append((fn, delta))
        self.last_ts = timestamp

    def close(self):
        if not self.closed:
            self.enter(self.start_timestamp + self.tottime, '')
            self.closed = True

    def get_scale_factor(self):
        scale_factor = 500 # 1 ms = 0.5px
        while self.tottime * scale_factor > 1000: # try to fit in 1000px
            scale_factor /= 2
        return scale_factor

    def get_marks(self):
        scale_factor = self.get_scale_factor()
        step = 0.1 # 1 second
        have_minor_ticks = True
        # space them at least 10px apart
        while step * scale_factor < 10:
            have_minor_ticks = False
            step *= 10
        time = step
        n = 1
        while time <= self.tottime:
            is_major = (n % 10 == 0) or not have_minor_ticks
            yield int(time * scale_factor), is_major
            time += step
            n += 1

    def render(self):
        self.close()
        html = []
        tottime = 1 if self.tottime == 0 else self.tottime
        scale_factor = self.get_scale_factor()
        error = 0
        for fn, time in self.parts:
            percent = 100 * time / tottime
            # I tried to use percentages, that didn't work well -- multiple
            # time bars did not align.  So we use pixels
            real_width = time * scale_factor
            px = int(real_width)
            error += (real_width - px)
            if error >= 1:
                px += 1
                error -= 1
            # border adds to an element's width, compensate
            # (but handle very tiny blocks too)
            border = 1 if px >= 2 else 0
            width = px - 2 * border
            # at least in chromium, width of inline-block elements apparently
            # doesn't include padding
            padding = min(width // 2, 3)
            width -= 2 * padding
            if width < 0: # pragma: nocover -- because this should never happen
                # do not raise anything, we don't want a debugging middleware
                # taking down the system just because something is a bit wrong
                print >> sys.stderr, 'Bug in logview.py: width < 0 (px=%r, border%r, padding=%r, width=%r)' % (px, border, padding, width)
            if not fn:
                bgcolor = '#444'
                fgcolor = best_contrast(bgcolor)
                html.append(
                    '<span style="display: inline-block; overflow: hidden;'
                                ' height: 15px; width: %(width)spx;'
                                ' padding: 4px %(padding)spx;">'
                    '&nbsp;'
                    '</span>'
                   % dict(
                       width=width,
                       padding=padding + border,
                       fgcolor=fgcolor,
                       bgcolor=bgcolor,
                   ))
            else:
                bgcolor = self.COLORS[hash(fn) % len(self.COLORS)]
                fgcolor = best_contrast(bgcolor)
                html.append(
                    '<span title="%(fn)s (%(percent)d%%, %(time)d ms)"'
                         ' style="display: inline-block; overflow: hidden;'
                                ' height: 15px; width: %(width)spx;'
                                ' background: %(bgcolor)s; color: %(fgcolor)s;'
                                ' border: outset %(bgcolor)s;'
                                ' border-width: 1px %(border)spx;'
                                ' position: relative;' # so it appears on top
                                                       # of time marks
                                ' padding: 3px %(padding)spx;">'
                    '%(text)s</span>'
                   % dict(
                       fn=fn,
                       text='%s&nbsp;(%d%%' % (fn, percent) if px > 8 else '&nbsp;',
                       time=time * 1000,
                       percent=percent,
                       width=width,
                       border=border,
                       padding=padding,
                       fgcolor=fgcolor,
                       bgcolor=bgcolor,
                   ))
        return ''.join(html)


def logview_filter_factory(global_conf, **kwargs):
    def filter(app):
        return LogviewMiddleware(app, global_conf, **kwargs)
    return filter
