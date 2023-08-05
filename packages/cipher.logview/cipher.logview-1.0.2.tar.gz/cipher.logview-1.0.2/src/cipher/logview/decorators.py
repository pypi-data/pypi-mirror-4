###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
Decorators for use with cipher.logview.

If you want a pretty request timeline above the logview, decorate some of your
view functions and methods with ::

    @cipher.logview.timed

"""

import functools
import inspect
import logging
import threading
import time


log = logging.getLogger('timeline')


def name_of(fn, args=()):
    """Return the name of a function.

    Try to figure out the class name as well, by peeking at the arguments
    supplied.

    Bugs: the class name may be inaccurate (you may see names of
    subclasses that inherit a method instead of the base class that
    defines it).  We may get better results if we use inspect.getsourcefile()
    and parse the AST to get the class containing a function with the
    given line number.  Or we can wait until Python 3 takes over and
    we can use fn.__qualname__.
    """
    name = fn.__name__
    argnames, varargs, varkw = inspect.getargs(fn.func_code)
    if args and argnames and argnames[0] == 'self':
        name = '%s.%s' % (args[0].__class__.__name__, name)
    return name


_indent_level = threading.local()


def timed(fn):
    """Decorator that logs function runtime with DEBUG level."""
    @functools.wraps(fn)
    def inner(*args, **kw):
        level = getattr(_indent_level, 'level', 0)
        fn_name = '- ' * level + name_of(fn, args)
        log.debug('%s entered', fn_name)
        _indent_level.level = level + 1
        started = time.time()
        try:
            return fn(*args, **kw)
        finally:
            duration = time.time() - started
            _indent_level.level = level
            log.debug('%s: %d ms', fn_name, duration * 1000)
    return inner
