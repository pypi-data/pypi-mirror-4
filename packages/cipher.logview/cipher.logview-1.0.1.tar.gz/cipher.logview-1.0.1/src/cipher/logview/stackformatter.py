###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
Replacement for traceback.format_stack that mentions the value of local
variables named ``__traceback_info__``.  This is a convention introduced by
Zope (e.g. zope.exceptions).

The other convention -- ``__traceback_supplement__`` is not supported.
"""

import linecache
import sys


def format_stack(f=None, limit=None):
    """Replacement for traceback.format_stack that supports __traceback_info__."""
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back
    return format_list(extract_stack(f, limit))


def extract_stack(f=None, limit = None):
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
        list.append((filename, lineno, name, line, tbi))
        f = f.f_back
        n += 1
    list.reverse()
    return list


def format_list(extracted_list):
    """Replacement for traceback.format_list that supports __traceback_info__"""
    list = []
    for filename, lineno, name, line, tbi in extracted_list:
        item = '  File "%s", line %d, in %s\n' % (filename, lineno, name)
        if line:
            item += '    %s\n' % line.strip()
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
