###############################################################################
#
# Portions Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007 Python
# Software Foundation; All Rights Reserved
# Portions Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
Replacement for traceback.format_stack and traceback.format_tb that
mentions the value of local variables named ``__traceback_info__``.  This
is a convention introduced by Zope (e.g. zope.exceptions).

The other convention -- ``__traceback_supplement__`` is also supported.
"""

import linecache
import sys


def format_stack(f=None, limit=None, traceback_supplement=False):
    """Replacement for traceback.format_stack that supports __traceback_info__."""
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back
    return format_list(extract_stack(f, limit, traceback_supplement))


def format_tb(tb=None, limit=None, traceback_supplement=True):
    """Replacement for traceback.format_tb that supports __traceback_info__."""
    return format_list(extract_tb(tb, limit, traceback_supplement=True))


def extract_stack(f=None, limit=None, traceback_supplement=False):
    """Replacement for traceback.extract_stack that supports __traceback_info__."""
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list = []
    n = 0
    while f is not None and (limit is None or n < limit):
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            line = line.strip()
        else:
            line = None
        tbi = f.f_locals.get('__traceback_info__', None)
        if traceback_supplement:
            tbs = f.f_locals.get('__traceback_supplement__',
                                 f.f_globals.get('__traceback_supplement__',
                                                 None))
        else:
            tbs = None
        list.append((filename, lineno, name, line, tbi, tbs))
        f = f.f_back
        n += 1
    list.reverse()
    return list


def extract_tb(tb, limit=None, traceback_supplement=True):
    """Replacement for traceback.extract_tb that supports __traceback_info__."""
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list = []
    n = 0
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            line = line.strip()
        else:
            line = None
        tbi = f.f_locals.get('__traceback_info__', None)
        if traceback_supplement:
            tbs = f.f_locals.get('__traceback_supplement__',
                                 f.f_globals.get('__traceback_supplement__',
                                                 None))
        else:
            tbs = None
        list.append((filename, lineno, name, line, tbi, tbs))
        tb = tb.tb_next
        n += 1
    return list


def format_list(extracted_list):
    """Replacement for traceback.format_list that supports __traceback_info__"""
    list = []
    for filename, lineno, name, line, tbi, tbs in extracted_list:
        item = '  File "%s", line %d, in %s\n' % (filename, lineno, name)
        if line:
            item += '    %s\n' % line.strip()
        if tbs:
            tbs_repr = ''
            try:
                factory, args = tbs[0], tbs[1:]
                supplement = factory(*args)
                for attr in ['source_url', 'line', 'column', 'expression']:
                    value = getattr(supplement, attr, None)
                    if value is not None:
                        tbs_repr += '     - %s: %s\n' % (
                                            attr, value)
                warnings = getattr(supplement, 'warnings', None)
                if warnings:
                    for warning in warnings:
                        tbs_repr += '     - %s: %s\n' % (
                                            'warning', warning)
                getInfo = getattr(supplement, 'getInfo', None)
                if getInfo is not None:
                    info = '\n' + str(getInfo())
                    info = info.replace('\n', '\n       ')
                    tbs_repr += '     - %s: %s\n' % ('getInfo()', info)
            except Exception, e:
                try:
                    tbs_repr += '     - <unrepresentable: %s>\n' % repr(e)
                except Exception:
                    tbs_repr += '     - <unrepresentable>\n'
            item += '   - __traceback_supplement__:\n%s' % tbs_repr
        if tbi:
            try:
                tbi_repr = str(tbi)
            except Exception, e:
                try:
                    tbi_repr = '<unrepresentable: %s>' % repr(e)
                except Exception:
                    tbi_repr = '<unrepresentable>'
            item += '   - __traceback_info__: %s\n' % tbi_repr
        list.append(item)
    return list
